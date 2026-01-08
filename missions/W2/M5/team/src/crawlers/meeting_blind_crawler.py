"""
블라인드에서 상견례 관련 게시물 글과 댓글들 수집
프로세스
1.블라인드에서 상견례 관련 게시글의 URL들을 수집
2. 각 게시물들을 순회하며 제목, 본문, 댓글들을 추출
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import yaml
import random
import pandas as pd
import os


def load_yaml(yaml_path):
    """
    YAML 설정 파일에서 크롤링에 필요한 설정값들을 로드
    """
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
        return config['url'], \
               config['max_scroll'], config['scroll_pause_time'],\
               config['data_path'], config['encoding'],\
               config['log_path']
    

def scroll_to_load_all_posts(driver, pause_time, max_scroll):
    """
    페이지를 스크롤하여 동적으로 로드되는 모든 게시물을 불러오기
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0

    while scroll_count < max_scroll:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time + random.random())

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height
        scroll_count += 1

    print(f"Total scrolls: #{scroll_count})")
    return


    
def extract(search_url, max_scroll, scroll_pause_time, data_path, encoding, logfile):
    """
    블라인드 검색 결과 페이지에서 게시물과 댓글을 크롤링하여 CSV로 저장
    """
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(search_url)
    time.sleep(3)

    scroll_to_load_all_posts(driver, max_scroll, scroll_pause_time)
    post_links = set()
    elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/kr/post/')]")
    for el in elements:
        href = el.get_attribute("href")
        if href:
            post_links.add(href)


    msg = f"Found {len(post_links)} posts"
    print(msg)
    logfile.write(msg+'\n')


    data = []
    count_comments = 0
    for idx, link in enumerate(post_links):
        driver.get(link)
        time.sleep(3)

        try:
            title = driver.find_element(By.CSS_SELECTOR, "h2").text
        except:
            title = ""

        try:
            content = driver.find_element(By.CSS_SELECTOR, "p.contents-txt").text.replace('\n', ' ')
        except:
            content = ""

        comments = []
        try:
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "p.cmt-txt")
            for c in comment_elements:
                if c.text.strip():
                    comments.append(c.text.replace('\n', ' '))
        except:
            pass

        count_comments += len(comments)

        data.append({
            "url": link,
            "title": title,
            "content": content,
            "comments_all": " || ".join(comments)
        })

        print(f"[{idx+1}/{len(post_links)}] Collected")
        time.sleep(1 + random.random())

        break

    df = pd.DataFrame(data)
    if not os.path.exists(data_path):
        df.to_csv(data_path, index=False, encoding=encoding)
    else:
        df.to_csv(data_path, index=False, mode='a', encoding=encoding, header=False)


    msg = f"Found {count_comments} comments"
    print(msg)
    logfile.write(msg+'\n')


    msg = "Done!"
    print(msg)
    logfile.write(msg+'\n')

    driver.quit()
    return

if __name__ == '__main__':
    yaml_path = '../config/blind_crawler.yaml'
    url, max_scroll, scroll_pause_time, data_path, encoding, log_path = load_yaml(yaml_path)
    logfile = open(log_path, "a+")

    extract(url, max_scroll, scroll_pause_time, data_path, encoding, logfile)