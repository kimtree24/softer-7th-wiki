"""
특정 키워드 검색의 네이버 블로그 글을 원하는 수만큼 가져오는 파일
프로세스 과정
1.네이버 API를 활용한 키워드 검색 상위 blog 게시물 url 추출
2. playwright를 활용해 URL 루프를 돌며 웹 크롤링 진행
"""

import os
import urllib.request
import urllib.parse
import json
import csv
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime

load_dotenv()

class NaverBlogCrawler:
    def __init__(self,
                 keyword: str,
                 display: int = 100,
                 max_results: int = 100,
                 batch_size: int = 50):

        self.keyword = keyword
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.display = min(display, 100)
        self.max_results = max_results
        self.batch_size = batch_size
        self.data_dir = Path("data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET must be set in .env file")

    def get_blog_urls(self):
        """네이버 API를 이용해 관련도순으로 블로그 게시글의 url 추출"""
        print(f"[INFO] Starting to fetch blog URLs for keyword: '{self.keyword}'")
        blog_urls = []
        start = 1

        while len(blog_urls) < self.max_results:
            encText = urllib.parse.quote(self.keyword)
            url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={self.display}&start={start}&sort=sim"

            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)

            try:
                response = urllib.request.urlopen(request)
                rescode = response.getcode()

                if rescode == 200:
                    response_body = response.read()
                    data = json.loads(response_body.decode('utf-8'))

                    items = data.get('items', [])
                    if not items:
                        print(f"[INFO] No more results found. Total collected: {len(blog_urls)}")
                        break

                    for item in items:
                        if len(blog_urls) >= self.max_results:
                            break
                        blog_urls.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'description': item.get('description', ''),
                            'bloggername': item.get('bloggername', ''),
                            'postdate': item.get('postdate', '')
                        })

                    print(f"[INFO] Collected {len(blog_urls)} URLs so far...")
                    start += self.display
                    time.sleep(0.1)
                else:
                    print(f"[ERROR] API Error Code: {rescode}")
                    break

            except Exception as e:
                print(f"[ERROR] Error fetching URLs: {e}")
                break

        print(f"[INFO] Total URLs collected: {len(blog_urls)}")
        return blog_urls[:self.max_results]

    def crawl_blog_content(self, url: str):
        """playwright를 활용해 블로그 게시글 내용 크롤링"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_timeout(2000)

                content = {
                    'url': url,
                    'title': '',
                    'content': '',
                    'date': '',
                    'crawled_at': datetime.now().isoformat()
                }

                iframe = page.query_selector('iframe#mainFrame')
                if iframe:
                    frame = iframe.content_frame()
                    if frame:
                        title_elem = frame.query_selector('.se-title-text, .pcol1, .se_title')
                        if title_elem:
                            content['title'] = title_elem.inner_text().strip()

                        content_elem = frame.query_selector('.se-main-container, .post-view, .__se_component_area')
                        if content_elem:
                            content['content'] = content_elem.inner_text().strip()

                        date_elem = frame.query_selector('.se_publishDate, .se-publish-date, .date')
                        if date_elem:
                            content['date'] = date_elem.inner_text().strip()

                browser.close()
                print(f"[SUCCESS] Crawled content from: {url}")
                return content

        except Exception as e:
            print(f"[ERROR] Failed to crawl {url}: {e}")
            return None

    def save_to_csv(self, data: list, filename: str = None):
        """크롤링한 데이터를 CSV 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.keyword}_{timestamp}.csv"

        filepath = self.data_dir / filename

        if not data:
            print("[WARNING] No data to save")
            return

        keys = data[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        print(f"[INFO] Data saved to: {filepath}")
        return filepath

    def save_batch_to_csv(self, data: list, filepath: Path, write_header: bool = False):
        """배치 데이터를 CSV 파일에 추가 저장"""
        if not data:
            return

        keys = data[0].keys()
        mode = 'w' if write_header else 'a'

        with open(filepath, mode, newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            if write_header:
                writer.writeheader()
            writer.writerows(data)

        print(f"[INFO] Saved batch of {len(data)} items to: {filepath}")

    def run(self):
        """전체 크롤링 프로세스 실행 (배치 저장 방식)"""
        print(f"\n{'='*60}")
        print(f"Starting Naver Blog Crawler")
        print(f"Keyword: {self.keyword}")
        print(f"Max Results: {self.max_results}")
        print(f"Batch Size: {self.batch_size}")
        print(f"{'='*60}\n")

        blog_urls = self.get_blog_urls()

        if not blog_urls:
            print("[WARNING] No URLs found to crawl")
            return None, None

        # CSV 파일 경로 미리 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.keyword}_{timestamp}.csv"
        filepath = self.data_dir / filename

        print(f"\n[INFO] Starting content crawling for {len(blog_urls)} URLs")
        print(f"[INFO] Saving in batches of {self.batch_size} items\n")

        batch_data = []
        total_saved = 0
        is_first_batch = True

        for idx, blog_info in enumerate(blog_urls, 1):
            print(f"[{idx}/{len(blog_urls)}] Crawling: {blog_info['link']}")

            content = self.crawl_blog_content(blog_info['link'])

            if content:
                combined_data = {**blog_info, **content}
                batch_data.append(combined_data)

            # 배치 크기에 도달하면 저장
            if len(batch_data) >= self.batch_size:
                self.save_batch_to_csv(batch_data, filepath, write_header=is_first_batch)
                total_saved += len(batch_data)
                print(f"[BATCH] Saved {len(batch_data)} items. Total saved: {total_saved}")
                batch_data = []  # 메모리 해제
                is_first_batch = False

            time.sleep(1)

        # 남은 데이터 저장
        if batch_data:
            self.save_batch_to_csv(batch_data, filepath, write_header=is_first_batch)
            total_saved += len(batch_data)
            print(f"[BATCH] Saved remaining {len(batch_data)} items. Total saved: {total_saved}")

        print(f"\n{'='*60}")
        print(f"[INFO] Crawling completed! Total items saved: {total_saved}")
        print(f"[INFO] File saved to: {filepath}")
        print(f"{'='*60}\n")

        return total_saved, filepath


if __name__ == "__main__":
    keyword = input("Enter search keyword: ")
    max_results = int(input("Enter number of posts to crawl (default 100): ") or 100)
    batch_size = int(input("Enter batch size for saving (default 50): ") or 50)

    crawler = NaverBlogCrawler(keyword=keyword, max_results=max_results, batch_size=batch_size)
    total_count, filepath = crawler.run()

    print(f"\nCrawling completed!")
    if total_count:
        print(f"Total posts crawled: {total_count}")
    if filepath:
        print(f"Data saved to: {filepath}")