#!/usr/bin/env python3
import sys

current_movie = None
title = None
rating_sum = 0.0
count = 0

def emit():
    if title is not None and count > 0:
        avg = rating_sum / count
        print(f"{title}\t{avg:.3f}")

for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue

    parts = line.split("\t", 1)
    if len(parts) != 2:
        continue

    movieId, value = parts
    parts2 = value.split("|", 1)
    if len(parts2) != 2:
        continue

    tag, data = parts2

    if movieId != current_movie:
        if current_movie is not None:
            emit()
        current_movie = movieId
        title = None
        rating_sum = 0.0
        count = 0

    if tag == "M":
        title = data
    elif tag == "R":
        try:
            rating_sum += float(data)
            count += 1
        except:
            pass

if current_movie is not None:
    emit()