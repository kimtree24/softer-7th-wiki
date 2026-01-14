#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split(",")

    # 헤더 스킵
    if parts[0] == "user_id":
        continue

    try:
        parent_asin = parts[1]
        rating = float(parts[2])

        # (상품ID, 평점)
        print(f"{parent_asin}\t{rating}")
    except:
        # 깨진 row, 누락 데이터 무시
        continue