#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    if row[0] == "userId":
        continue

    movieId = row[1]
    rating = row[2]

    print(f"{movieId}\tR|{rating}")