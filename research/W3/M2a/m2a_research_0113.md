## 1. Docker에서 FROM ubuntu는 OS인가
- Docker 이미지는 커널을 포함하지 않음.
- FROM ubuntu:22.04는 부팅 가능한 OS가 아니라 **Ubuntu 사용자 공간(rootfs)**

```
Docker Image = root filesystem + 라이브러리 + 쉘 + 패키지
```

커널은 **호스트의 리눅스 커널을 공유**
그래서
- systemd 없음
- 부팅 없음
- PID 1 = CMD로 실행한 프로세스

---

## 2. eclipse-temurin vs ubuntu
FROM eclipse-temurin:8-jdk는 Java가 포함된 **최소 리눅스 환경** 
Hadoop은 Java만 필요하므로 ubuntu보다 가벼운 eclipse-temurin 선택

---

## 3. JAVA_HOME 에러의 정체
Hadoop은 내부 스크립트에서 다음을 실행함.
```
$JAVA_HOME/bin/java
```
eclipse-temurin에서는:
```
JAVA_HOME=/opt/java/openjdk
```
이를 반드시 hadoop-env.sh에 설정해야 함

---

## 4. root로 실행 시 HDFS 오류
Hadoop은 원래 `hdfs`, `yarn`, `mapred` 유저로 실행되도록 설계됨.  
Docker에서는 root로 실행되므로 아래 우회가 필요

```
HDFS_NAMENODE_USER=root
HDFS_DATANODE_USER=root
YARN_RESOURCEMANAGER_USER=root
YARN_NODEMANAGER_USER=root
```

---

## 5. Master / Worker 역할 분리
| 역할 | 서비스 |
|---|---|
| Master | NameNode, ResourceManager |
| Worker | DataNode, NodeManager |

이미지 구조:
```
hadoop-base
  ├─ hadoop-master
  └─ hadoop-worker
```
컨테이너:
```
namenode(master), worker1, worker2
```

---

## 6. 같은 Docker 네트워크의 의미
Hadoop은 hostname으로 통신
```
worker1 → namenode:9000
worker2 → namenode:8032
```
따라서 docker-compose에서 **같은 네트워크**가 필수

---

## 7. hostname = Hadoop host
`fs.defaultFS = hdfs://namenode:9000` 이라면  
docker-compose의 hostname도 `namenode`여야 합니다.

---

## 8. DataNode hostname 설정
Docker IP는 재시작 시 바뀜 
따라서 HDFS는 hostname을 사용해야 함

```xml
dfs.datanode.use.datanode.hostname=true
dfs.client.use.datanode.hostname=true
```

---

## 9. SafeMode
NameNode는 부팅 후 블록 확인 전까지 쓰기 금지(SafeMode)입니다.
필요 시:
```
hdfs dfsadmin -safemode leave
```

---

## 10. mapreduce_shuffle 오류
YARN에서 MapReduce Shuffle 서비스 등록 필요:

```xml
yarn.nodemanager.aux-services=mapreduce_shuffle
yarn.nodemanager.aux-services.mapreduce.shuffle.class=org.apache.hadoop.mapred.ShuffleHandler
```

---

## 11. getconf vs 실제 HDFS
- `getconf` → 설정 파일만 확인
- `hdfs dfs` → NameNode에 실제 연결  
네트워크가 깨지면 getconf는 PASS, hdfs는 FAIL 가능

---

## 12. M2a vs M2b
| M2a | M2b |
|---|---|
| 설정을 이미지에 bake | 설정을 볼륨으로 마운트 |
| docker build 필요 | XML 수정 후 재시작 |
| 개발자 관점 | 운영자 관점 |