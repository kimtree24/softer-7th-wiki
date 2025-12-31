import pandas as pd
import json
import os

# World bank에서 다운받은 국가별 Region Data를 json으로 변환
# https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups?utm_source=chatgpt.com

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCEL_PATH = os.path.join(BASE_DIR, "row_data", "world_bank_region_data.xlsx")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "row_data", "Region_row.json")

df = pd.read_excel(EXCEL_PATH)

# 필요한 컬럼만 가져옴
df = df[["Economy", "Region"]]

# Region 없는 데이터 제거
df = df.dropna(subset=["Region"])

country_region = {
    row["Economy"].strip(): row["Region"].strip()
    for _, row in df.iterrows()
}

# json 저장
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(country_region, f, ensure_ascii=False, indent=2)