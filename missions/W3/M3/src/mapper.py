#!/usr/bin/env python3
import sys
import re

# Hadoop Streaming:
# STDIN  -> HDFS input split
# STDOUT -> shuffle 단계로 전달됨

for line in sys.stdin:
    # 소문자 변환
    line = line.lower()

    # 단어만 추출 (알파벳 기준)
    words = re.findall(r"[a-z]+", line)

    for word in words:
        print(f"{word}\t1")