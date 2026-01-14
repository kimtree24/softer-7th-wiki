# Hadoop MapReduce 워드카운트

## 사용한 전자책
- **제목**: War and Peace
- **저자**: Leo Tolstoy
- **출처**: Project Gutenberg
- **URL**: https://www.gutenberg.org/ebooks/2600

## 디렉토리 구조
```
M3/
├── data/
│   └── ebook.txt
├── src/
│   ├── mapper.py
│   └── reducer.py
├── docker-compose.yml
└── README.md
```

## 0. 클러스터 초기 실행

```bash
docker-compose up -d
```

---

## 1. HDFS에 입력 파일 업로드
```bash
hdfs dfs -mkdir -p /wordcount/input
hdfs dfs -put /data/ebook.txt /wordcount/input
hdfs dfs -ls /wordcount/input
```

## 2. MapReduce 작업 실행
```bash
hdfs dfs -rm -r -f /wordcount/output
cd /src
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /wordcount/input \
  -output /wordcount/output \
  -mapper mapper.py \
  -reducer reducer.py \
  -file mapper.py \
  -file reducer.py
```

## 3. 작업 모니터링
웹 브라우저에서 다음 주소로 진행 상황 확인:
```
http://localhost:8088
```

## 4. 결과 조회 및 다운로드
```bash
hdfs dfs -ls /wordcount/output
hdfs dfs -cat /wordcount/output/part-00000 | head
hdfs dfs -get /wordcount/output /data/result
