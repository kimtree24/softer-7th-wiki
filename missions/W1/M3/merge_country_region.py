import json
import os

# GDP 스크래핑 데이터 기준으로 world_bank_region 데이터 merge

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GDP_PATH = os.path.join(BASE_DIR, "row_data", "Countries_by_GDP.json")
REGION_PATH = os.path.join(BASE_DIR, "row_data", "country_region_map.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "row_data", "gdp_country_region_merged.json")


# JSON 로드
with open(GDP_PATH, "r", encoding="utf-8") as f:
    gdp_data = json.load(f)

with open(REGION_PATH, "r", encoding="utf-8") as f:
    region_data = json.load(f)


# GDP 기준으로 region 매핑
merged_country_region = {}

for country in gdp_data.keys():
    if country in region_data:
        # region 정보가 있는 경우
        merged_country_region[country] = region_data[country]
    else:
        # region 정보가 없는 경우 (수동 입력 대상)
        merged_country_region[country] = None


# 결과 저장
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(merged_country_region, f, ensure_ascii=False, indent=2)