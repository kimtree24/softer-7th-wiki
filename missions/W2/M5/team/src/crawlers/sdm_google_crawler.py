"""
구글 검색을 통해 스드메(스튜디오, 드레스, 메이크업) 관련된 사이트들의 텍스트들을 가져오는 파일
프로세스 과정
1. Google 검색 결과 페이지를 순회하며 제목, 요약, 상세 페이지 URL
2. URL을 이용해 상세 페이지의 본문을 수집
3. 불필요 태그 등을 제거 후 파일에 저장
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from readability import Document
import requests
import time
import pandas as pd


# ======================
# 기본 설정
# ======================
CRAWL_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

GOOGLE_SEARCH_URL_TEMPLATE = "https://www.google.com/search?q={query}&hl=ko&start={start}"


# ======================
# 상세 페이지 본문 추출 - 구글 검색 페이지에서 가져온 url을 바탕으로 해당 url 이동 후 크롤링
# ======================
def crawl_page_body_from_google_url(url, timeout=15):
    """readability-lxml 기반 본문 텍스트 추출"""
    try:
        resp = requests.get(url, headers=CRAWL_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"상세 페이지 요청 실패: {url} | {e}")
        return ""

    try:
        doc = Document(resp.text)
        content_html = doc.summary(html_partial=True)
    except Exception as e:
        print(f"readability 파싱 실패: {url} | {e}")
        return ""

    soup = BeautifulSoup(content_html, "html.parser")

    # 불필요 태그 제거
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text


# ======================
# Google 검색 크롤러
# ======================
def google_search_crawler_selenium(query, max_pages, delay):
    """
    Google 검색 결과 페이지를 Selenium으로 순회하며
    - 검색 결과 제목
    - 검색 결과 요약(snippet)
    - 상세 페이지 URL
    - 상세 페이지 본문(body text)
    을 수집하는 크롤러 함수
    """
    
    results = [] # 수집된 결과를 담을 리스트
    
    # Selenium Chrome 설정
    chrome_options = Options()
    # 자동화 탐지 최소화 (Google 차단 회피 목적)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")

    # Chrome WebDriver 실행
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # 검색 결과 페이지 순회
        for page in range(max_pages):
            # Google 검색 페이지는 start 파라미터로 페이지네이션
            start = page * 10
            url = GOOGLE_SEARCH_URL_TEMPLATE.format(
                query=query,
                start=start
            )

            print(f"\n{page + 1}페이지 수집 중")
            driver.get(url)

            # 검색 결과 영역 로딩 대기
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "search"))
            )

            time.sleep(2)

            # 현재 페이지 HTML 파싱
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # 검색 결과 영역 추출
            search_area = soup.select_one("div#search")
            if not search_area:
                print("search 영역 없음")
                continue
            
            # Google 검색 결과의 개별 블록
            blocks = search_area.select("div.MjjYud")
            print(f"   → 검색 결과 블록 {len(blocks)}개 발견")

            # 각 검색 결과 블록 처리
            for b in blocks:
                # 검색 결과 제목
                title_el = b.find("h3")
                if not title_el:
                    continue

                search_title = title_el.get_text(strip=True)

                # 검색 결과 요약글
                snippet_el = (
                    b.select_one("div.VwiC3b") or
                    b.select_one("span.YrbPuc")
                )
                search_snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""

                # 상세 페이지 URL
                link_el = b.select_one("div.yuRUbf a[jsname='UWckNb']")
                if not link_el:
                    continue

                detail_url = link_el.get("href")
                if not detail_url or not detail_url.startswith("http"):
                    continue

                print(f"      상세 페이지 수집: {detail_url}")

                # 상세 페이지 본문 크롤링
                body_text = crawl_page_body_from_google_url(detail_url)

                # 수집 결과 저장
                results.append({
                    "query": query,
                    "page": page + 1,
                    "search_title": search_title,
                    "search_snippet": search_snippet,
                    "url": detail_url,
                    "body_text": body_text
                })

                time.sleep(1)  # 상세 페이지 부하 방지

            time.sleep(delay)

    finally:
        driver.quit()

    return results


# ======================
# pandas 기반 CSV 저장
# ======================
def save_to_csv_pandas(data, filename="wedding_sdm_crawl.csv"):
    if not data:
        print("저장할 데이터가 없습니다.")
        return

    df = pd.DataFrame(data)

    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"\nCSV 저장 완료: {filename}")


# ======================
# 실행부
# ======================
if __name__ == "__main__":
    
    # 검색어
    queries = [
        "결혼 스드메 준비 과정",
        "스드메 업체 선택 기준",
        "스드메 후기",
        "스드메 추가금 후기",
        "웨딩 드레스 후기",
        "웨딩 메이크업 후기",
        "스드메 계약 시 주의사항",
    ]

    all_data = []

    for q in queries:
        print(f"\n=== 쿼리 시작: {q} ===")
        data = google_search_crawler_selenium(
            query=q,
            max_pages=30,
            delay=3
        )
        all_data.extend(data)

    print(f"\n총 수집 결과 수: {len(all_data)}")
    save_to_csv_pandas(all_data, filename="wedding_sdm_crawl.csv")