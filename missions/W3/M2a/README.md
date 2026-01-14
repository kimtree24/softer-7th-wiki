# Docker 기반 Hadoop 멀티 노드 클러스터

## 개요
이 프로젝트는 Docker를 사용해 **멀티 노드 Hadoop 클러스터**(1 Master, 2 Workers)를 구성하고,  
HDFS 분산 저장과 YARN 기반 분산 처리를 검증한다.

구성:
- Master: NameNode + ResourceManager
- Worker1, Worker2: DataNode + NodeManager

## 1. Docker 이미지 빌드
```bash
docker build -t hadoop-base docker/base
docker build -t hadoop-master docker/master
docker build -t hadoop-worker docker/worker
```

---

## 2. 클러스터 실행
```bash
docker-compose up -d
```

컨테이너 확인:
```bash
docker ps
```

---

## 3. HDFS 기본 작업 (Master에서)
```bash
docker exec -it master bash
```

### 디렉토리 생성
```bash
hdfs dfs -mkdir /test
```

### 파일 업로드
```bash
echo "hello hadoop" > sample.txt
hdfs dfs -put sample.txt /test/
```

### 파일 목록
```bash
hdfs dfs -ls /test
```

### 파일 다운로드
```bash
hdfs dfs -get /test/sample.txt ./downloaded.txt
cat downloaded.txt
```

---

## 4. MapReduce 샘플 실행
WordCount 예시:
```bash
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /test /output
hdfs dfs -cat /output/part-r-00000
```

YARN UI(8088)에서 Job이 worker 노드에서 실행되는지 확인 가능.

---

## 5. 데이터 영속성
다음 볼륨이 HDFS 데이터를 보존한다:
- `./data/namenode` → `/hadoop/dfs/name`
- `./data/datanode1` → `/hadoop/dfs/data` (worker1)
- `./data/datanode2` → `/hadoop/dfs/data` (worker2)

컨테이너 재시작 후에도 데이터 유지됨.

---

## 6. 종료 및 재시작
```bash
docker-compose down
docker-compose up -d
```
