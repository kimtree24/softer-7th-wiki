# import
import os
import re
import json
import sqlite3
import logging
from datetime import date

import requests
import pandas as pd
from bs4 import BeautifulSoup

# ======================
# PATH 지정
# ======================

# 최상단 PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DB 경로
DB_PATH = os.path.join(BASE_DIR, "db", "World_Economies.db")
# Extract row data 경로
RAW_PATH = os.path.join(BASE_DIR, "row_data", "Countries_by_GDP.json")
# 로그 경로
LOG_PATH = os.path.join(BASE_DIR, "logs", "etl_project_log.txt")
# Region 파일 경로
REGION_JSON_PATH = os.path.join(BASE_DIR, "row_data", "Region_fixed.json")

# 디렉토리 없는 경우 생성
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# ======================
# 로깅
# ======================

def setup_logger(log_path, logger_name) -> logging.Logger:

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # 중복 핸들러 방지
    if logger.handlers:
        return logger

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s || %(message)s",
        datefmt="%Y-%B-%d-%H-%M-%S"
    )

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)

    return logger

# ======================
# extract
# ======================

def extract_gdp():
    URL = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29"

    # 헤더 같이 안보내면 스크래핑 불가
    headers = { "User-Agent": "Mozilla/5.0" }
    
    logger.info("Extract started")
    
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 타겟 테이블만 파싱
    table = soup.select_one(
        "table.wikitable.sortable.sticky-header-multi.static-row-numbers"
    )
    
    result_dict = {}

    # 테이블에서 row 단위로 파싱
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")

        # td가 2개 이상인 행만 처리
        if len(tds) < 2:
            continue

        # 국가명 추출
        country_tag = tds[0]
        country= country_tag.find_all("a")
        
        # 주석 달린 컬럼 처리 위한 로직 -> 주석 무시하고 국가명만 파싱
        if len(country) != 0:
            country_name = country[0].get_text(strip=True)
        else:
            country_name = country_tag.get_text(strip=True)

        # IMF GDP 추출
        imf_gdp_raw = tds[1].get_text(strip=True)

        result_dict[country_name] = imf_gdp_raw
    
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    logger.info("Extract finished")

# ======================
# transform
# ======================

# gdp값 전처리
def parse_gdp_and_year(value):
    # 값이 없는 경우 None처리
    if not value or value == "—N/a":
        return None, None

    # 숫자 추출
    number_match = re.search(r"[\d,]+", value)
    if not number_match:
        return None, None

    gdp_million = int(number_match.group().replace(",", ""))
    gdp_billion = round(gdp_million / 1000, 2)

    # 연도 추출 (괄호 안 4자리 숫자) -> gdp 기준 값이 다른 경우 처리
    year_match = re.search(r"\((\d{4})\)", value)
    # 기준 연도가 다르다면 ()안의 연도로 변환
    if year_match:
        year = int(year_match.group(1))
    # 기본적으로는 현재 날짜
    else:
        year = date.today().year

    return gdp_billion, year

# transform -> 디비 적재 용이한 형태로 가공
def transform_gdp():
    logger.info("Transform started")
    
    # extract한 데이터 파일 읽어오기
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # etl 실행한 날짜 DB에 함께 적재하여 관리
    today = date.today().isoformat()
    transformed = []

    for country, gdp in raw_data.items():
        # 국가 단위 아닌 것 제거
        if country.lower() == "world":
            continue
        
        # gdp값과 기준 연도 분리
        gdp_billion, year = parse_gdp_and_year(gdp)
        if gdp_billion is None:
            continue
        
        # DB 적재 용이한 구조로 변환
        transformed.append({
            "country": country.title(),
            "gdp_usd_billion": gdp_billion,
            "year": year,
            "update_date": today
        })
        
    df = pd.DataFrame(transformed)
    logger.info("Transform finished")
    return df

# ======================
# load
# ======================

# gdp 데이터 테이블 생성 및 적재
def load_gdp(df):
    logger.info("Load started")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Countries_by_GDP (
            country TEXT,
            year INTEGER,
            gdp_usd_billion REAL,
            update_date TEXT,
            PRIMARY KEY (country, year)
        )
    """)

    # GDP 기준 정렬
    df = df.sort_values("gdp_usd_billion", ascending=False)

    # 중복되는 값은 무시 (country, year 기준)
    insert_sql = """
        INSERT OR IGNORE INTO Countries_by_GDP
        (country, year, gdp_usd_billion, update_date)
        VALUES (?, ?, ?, ?)
    """

    data = [
        (
            row["country"],
            int(row["year"]),
            float(row["gdp_usd_billion"]),
            row["update_date"]
        )
        for _, row in df.iterrows()
    ]

    cursor.executemany(insert_sql, data)
    conn.commit()
    conn.close()

    logger.info(f"Load finished - attempted {len(data)} rows")

# region 데이터 테이블 생성 및 적재
def load_region():
    logger.info("Region Load started")

    with open(REGION_JSON_PATH, "r", encoding="utf-8") as f:
        region_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Region (
            country TEXT PRIMARY KEY,
            region TEXT
        )
    """)

    insert_sql = """
        INSERT OR REPLACE INTO Region (country, region)
        VALUES (?, ?)
    """

    data = [
        (country, region)
        for country, region in region_data.items()
        if country.lower() != "world"
    ]

    cursor.executemany(insert_sql, data)
    conn.commit()
    conn.close()

    logger.info(f"Region Load finished - {len(data)} rows")


# ======================
# print sql result
# ======================

# 100불 이상 국가 출력
def print_gdp_over_100b():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        g.country,
        r.region,
        g.gdp_usd_billion
    FROM Countries_by_GDP g
    LEFT JOIN Region r
        ON g.country = r.country
    WHERE g.gdp_usd_billion >= 100
    ORDER BY g.gdp_usd_billion DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("\n --- GDP ≥ 100B USD Countries ---")
    print(df.to_string(index=False))
    
# Region 별 top5 국가 gdp 평균
def print_region_top5_avg():
    conn = sqlite3.connect(DB_PATH)

    query = """
    WITH ranked_gdp AS (
        SELECT
            g.country,
            r.region,
            g.gdp_usd_billion,
            ROW_NUMBER() OVER (
                PARTITION BY r.region
                ORDER BY g.gdp_usd_billion DESC
            ) AS rank_num
        FROM Countries_by_GDP g
        JOIN Region r
            ON g.country = r.country
        WHERE r.region IS NOT NULL
    )
    SELECT
        region,
        AVG(gdp_usd_billion) AS avg_gdp_top5
    FROM ranked_gdp
    WHERE rank_num <= 5
    GROUP BY region
    ORDER BY avg_gdp_top5 DESC;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("\n --- Region별 Top5 GDP 평균 ---")
    print(df.to_string(index=False))


# ======================
# main
# ======================
if __name__ == "__main__":
    # 로깅 모듈 설정
    logger = setup_logger(LOG_PATH, "etl_logger")
    
    # extract
    extract_gdp()
    
    # transform
    df = transform_gdp()
    
    # load
    load_gdp(df)
    
    # region load
    load_region()
    
    print_gdp_over_100b()
    print_region_top5_avg()