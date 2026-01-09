"""
Google 검색 → 스드메 관련 URL 수집 → 병렬 본문 크롤링 → CSV 저장

아키텍처
1. Selenium으로 Google 검색 결과에서 URL만 수집
2. multiprocessing.Pool로 URL을 병렬로 크롤링
3. readability-lxml로 본문 추출
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
from multiprocessing import Pool, cpu_count
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
# Selenium → Google에서 URL만 수집
# ======================
def collect_google_urls(query, max_pages, delay):
    urls = []

    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        options=chrome_options
    )

    try:
        for page in range(max_pages):
            start = page * 10
            url = GOOGLE_SEARCH_URL_TEMPLATE.format(query=query, start=start)

            print(f"[Google] {query} | {page+1}페이지")
            driver.get(url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "search"))
            )

            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            blocks = soup.select("div.MjjYud")

            for b in blocks:
                link = b.select_one("div.yuRUbf a[jsname='UWckNb']")
                if link:
                    href = link.get("href")
                    if href and href.startswith("http"):
                        urls.append({
                            "query": query,
                            "url": href
                        })

            time.sleep(delay)

    finally:
        driver.quit()

    print(f"[Google] {query} → {len(urls)}개 URL 수집 완료")
    return urls


# ======================
# 단일 URL → 본문 추출 (Pool에서 실행됨)
# ======================
def crawl_single_url(item):
    url = item["url"]
    query = item["query"]

    try:
        resp = requests.get(url, headers=CRAWL_HEADERS, timeout=15)
        resp.raise_for_status()

        doc = Document(resp.text)
        html = doc.summary(html_partial=True)

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        text = soup.get_text(" ", strip=True)

        return {
            "query": query,
            "url": url,
            "body_text": text
        }

    except Exception as e:
        print(f" 실패: {url} | {e}")
        return None


# ======================
# Pool로 URL 병렬 크롤링
# ======================
def crawl_urls_parallel(url_list):
    print(f"\n[Pool] 본문 크롤링 시작 ({len(url_list)}개)")

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(crawl_single_url, url_list)

    results = [r for r in results if r]
    print(f"[Pool] 성공: {len(results)}개")

    return results


# ======================
# 실행부
# ======================
if __name__ == "__main__":

    queries = [
        "결혼 스드메 후기",
    ]

    all_urls = []

    # 1단계: Google에서 URL 수집
    for q in queries:
        urls = collect_google_urls(q, max_pages=10, delay=2)
        all_urls.extend(urls)

    print(f"\n총 URL 수집 개수: {len(all_urls)}")

    # 2단계: 병렬 본문 크롤링
    all_data = crawl_urls_parallel(all_urls)

    # 3단계: CSV 저장
    df = pd.DataFrame(all_data)
    df.to_csv("wedding_sdm_parallel.csv", index=False, encoding="utf-8-sig")

    print("\nCSV 저장 완료 → wedding_sdm_parallel.csv")