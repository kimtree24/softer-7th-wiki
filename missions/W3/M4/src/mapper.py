#!/usr/bin/env python3
import sys
import re

POS_WORDS = {
    "good","great","love","awesome","amazing","happy","nice","best",
    "wonderful","fantastic","excellent","cool","enjoy","yay","lol",
    "thanks","thank","perfect"
}
NEG_WORDS = {
    "bad","terrible","hate","awful","horrible","sad","worst","angry",
    "annoying","disappointed","pain","sucks","suck","wtf","ugh",
    "sorry","fail","broken"
}

WORD_RE = re.compile(r"[a-zA-Z']+")

def classify(text: str) -> str:
    tokens = [t.lower() for t in WORD_RE.findall(text)]
    pos = sum(1 for t in tokens if t in POS_WORDS)
    neg = sum(1 for t in tokens if t in NEG_WORDS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"

for bline in sys.stdin.buffer:
    # 인코딩 깨져도 동작하도록
    line = bline.decode("utf-8", errors="ignore").strip()
    if not line:
        continue

    parts = line.split(",", 5)
    if len(parts) < 6:
        continue

    text = parts[5]
    sentiment = classify(text)
    sys.stdout.write(f"{sentiment}\t1\n")