# M1 제출물 – Docker 기반 Single‑Node Hadoop 클러스터

## 실행 방법

### 1. Docker 이미지 빌드
```bash
docker build -t hadoop-single-node .
```

### 2. 컨테이너 실행
```bash
docker run -it --name hadoop \
  -p 9870:9870 -p 9000:9000 -p 9864:9864 -p 8088:8088 \
  -v $(pwd)/hdfs_data:/hadoop/dfs \
  hadoop-single-node
```

### 3. Hadoop 서비스 확인
```bash
docker exec -it hadoop bash
jps
```

## HDFS 사용 예제

```bash
su - hadoop
export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

hdfs dfs -mkdir /test
echo "Hello Hadoop" > sample.txt
hdfs dfs -put sample.txt /test/
hdfs dfs -get /test/sample.txt downloaded.txt
cat downloaded.txt
```

## Web UI
- NameNode UI: http://localhost:9870
- YARN UI: http://localhost:8088

## 데이터 영속성
컨테이너 삭제 후 재실행해도 `./hdfs_data`에 저장된 HDFS 데이터는 유지된다.
