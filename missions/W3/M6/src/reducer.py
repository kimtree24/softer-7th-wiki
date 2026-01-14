#!/usr/bin/env python3
import sys

current_asin = None
total_rating = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    asin, rating = line.split("\t")
    rating = float(rating)

    if current_asin == asin:
        total_rating += rating
        count += 1
    else:
        if current_asin is not None:
            avg = total_rating / count
            print(f"{current_asin}\t{count}\t{avg:.2f}")

        current_asin = asin
        total_rating = rating
        count = 1

# 마지막 상품 출력
if current_asin is not None:
    avg = total_rating / count
    print(f"{current_asin}\t{count}\t{avg:.2f}")