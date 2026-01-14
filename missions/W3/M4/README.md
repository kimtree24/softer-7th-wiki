# Sentiment140 Hadoop MapReduce 프로젝트 README

## 1. 개요
이 프로젝트는 Apache Hadoop과 Hadoop Streaming(MapReduce)을 이용하여 Sentiment140 트위터 데이터셋의 감성을 분석합니다.
Python 기반 Mapper와 Reducer를 사용하여 각 트윗을 positive, negative, neutral로 분류하고 HDFS에 결과를 저장합니다.

## 2. 하둡 클러스터 실행
```bash
docker compose up -d
```

## 3. 데이터셋 HDFS 업로드
```bash
hdfs dfs -mkdir -p /datasets/sentiment140
hdfs dfs -put -f /data/twitter.csv /datasets/sentiment140/twitter.csv
hdfs dfs -ls /datasets/sentiment140
```

## 4. Mapper / Reducer 준비
```bash
cd /src
chmod +x mapper.py reducer.py
```

## 5. MapReduce 실행
```bash
hdfs dfs -rm -r -f /outputs/sentiment140_sentiment_counts

hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
  -files /src/mapper.py#mapper.py,/src/reducer.py#reducer.py \
  -mapper "python3 ./mapper.py" \
  -reducer "python3 ./reducer.py" \
  -input /datasets/sentiment140/twitter.csv \
  -output /outputs/sentiment140_sentiment_counts
```

## 6. 작업 모니터링
```bash
yarn application -list
```

## 7. 결과 확인
```bash
hdfs dfs -ls /outputs/sentiment140_sentiment_counts
hdfs dfs -cat /outputs/sentiment140_sentiment_counts/part-00000
```

## 8. 결과 검증
```bash
hdfs dfs -cat /datasets/sentiment140/training.csv | wc -l
hdfs dfs -cat /outputs/sentiment140_sentiment_counts/part-00000 | awk '{sum+=$2} END {print sum}'
```

두 값이 거의 같으면 성공

## 9. 로컬로 결과 다운로드
```bash
hdfs dfs -get /outputs/sentiment140_sentiment_counts ./sentiment_result
cat ./sentiment_result/part-00000
```