# MovieLens 20M 데이터셋 기반 영화별 평균 평점 계산

## 1. 데이터셋
MovieLens 20M Dataset

사용 파일:
- ratings.csv (userId, movieId, rating, timestamp)
- movies.csv (movieId, title, genres)

## 2. 하둡 클러스터 실행
```bash
docker compose up -d
```

## 3. HDFS 업로드
```bash
hdfs dfs -mkdir -p /datasets/movielens
hdfs dfs -put data/ratings.csv /datasets/movielens/
hdfs dfs -put data/movies.csv /datasets/movielens/
```

## 4. Hadoop Streaming 실행
```bash
hdfs dfs -rm -r /outputs/movielens_avg 2>/dev/null

hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar   -files mapper.py,reducer.py   -mapper "python3 mapper.py"   -reducer "python3 reducer.py"   -input /datasets/movielens/ratings.csv   -output /outputs/movielens_avg
```

## 5. 결과 확인
```bash
hdfs dfs -ls /outputs/movielens_avg
hdfs dfs -cat /outputs/movielens_avg/part-00000 | head
```

출력 형식:
```
title    average_rating
```

## 6. 결과 다운로드
```bash
hdfs dfs -get /outputs/movielens_avg/part-00000 ./movielens_avg.txt
```

## 7. 검증 방법
특정 movieId에 대해 직접 평균을 계산하여 결과를 검증할 수 있다.
```bash
hdfs dfs -cat /datasets/movielens/ratings.csv | grep ",1," | awk -F',' '{sum+=$3; n++} END {print sum/n}'
```
