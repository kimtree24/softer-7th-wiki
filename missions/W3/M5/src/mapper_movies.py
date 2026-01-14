#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    if row[0] == "movieId":
        continue

    movieId = row[0]
    title = row[1]

    print(f"{movieId}\tM|{title}")