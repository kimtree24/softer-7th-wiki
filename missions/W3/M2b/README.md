# W3 M2b – Hadoop Multi-Node Cluster 설정 자동화 & 검증

본 과제는 Docker 기반 Apache Hadoop 멀티 노드 클러스터에서  
**설정 변경을 자동화하고, 변경 결과를 검증하는 시스템**을 구현하는 것이 목표입니다.

M2a에서는 Hadoop 클러스터를 구축했고,  
M2b에서는 그 클러스터의 설정을 **스크립트로 변경 & 검증**하는 과제를 수행합니다.

---

## 📌 과제 목표

- Hadoop 멀티 노드 클러스터(Docker 기반) 구성
- core-site.xml, hdfs-site.xml, mapred-site.xml, yarn-site.xml 설정 자동 수정
- 수정된 설정이 실제 Hadoop에 반영되었는지 자동 검증
- 설정 백업, 재시작, 검증을 하나의 자동화 흐름으로 구성

---

## 🧩 시스템 구조

```
Mac Host
 ├── docker-compose.yml
 ├── config/                ← Hadoop 설정 파일 (볼륨 마운트)
 │     ├── core-site.xml
 │     ├── hdfs-site.xml
 │     ├── mapred-site.xml
 │     └── yarn-site.xml
 ├── modify-config.py       ← 설정 변경 스크립트
 ├── verify-config.py       ← 설정 검증 스크립트
 └── docker containers
        ├── master (NameNode + ResourceManager)
        ├── worker1 (DataNode + NodeManager)
        └── worker2 (DataNode + NodeManager)
```

Hadoop 설정 디렉토리(`/opt/hadoop/etc/hadoop`)는 Docker 볼륨으로  
호스트의 `config/` 디렉토리에 마운트되어 있습니다.  
따라서 **호스트에서 XML을 수정하면 컨테이너에 즉시 반영**됩니다.

---

## ⚙ 설정 변경 대상

| 파일 | 변경 항목 | 값 |
|------|---------|----|
| core-site.xml | fs.defaultFS | hdfs://namenode:9000 |
| | hadoop.tmp.dir | /hadoop/tmp |
| | io.file.buffer.size | 131072 |
| hdfs-site.xml | dfs.replication | 2 |
| | dfs.blocksize | 134217728 |
| | dfs.namenode.name.dir | /hadoop/dfs/name |
| mapred-site.xml | mapreduce.framework.name | yarn |
| | mapreduce.jobhistory.address | namenode:10020 |
| | mapreduce.task.io.sort.mb | 256 |
| yarn-site.xml | yarn.resourcemanager.address | namenode:8032 |
| | yarn.nodemanager.resource.memory-mb | 8192 |
| | yarn.scheduler.minimum-allocation-mb | 1024 |

---

## 🛠 실행 방법

### 1️⃣ 클러스터 초기 실행

```bash
docker-compose up -d
```

---

### 2️⃣ 설정 변경 실행

```bash
python3 modify-config.py ./config
```

수행 작업:
- `config_backup/`에 기존 XML 백업
- XML 값 수정
- Hadoop 서비스 재시작 (stop-dfs, stop-yarn → start-dfs, start-yarn)

---

### 3️⃣ 설정 검증 실행

```bash
python3 verify-config.py
```

확인 내용:
- hdfs getconf / mapred getconf / yarn getconf 값 비교
- HDFS 테스트 파일 생성
- 복제 계수 확인
- MapReduce WordCount 실행 (YARN 사용 여부)
- ResourceManager 메모리 설정 확인

---

## 📊 기대 출력 예시

```
PASS: [hdfs getconf fs.defaultFS] -> hdfs://namenode:9000
PASS: [hdfs getconf hadoop.tmp.dir] -> /hadoop/tmp
PASS: [hdfs getconf io.file.buffer.size] -> 131072
PASS: [hdfs getconf dfs.replication] -> 2
PASS: [hdfs getconf dfs.blocksize] -> 134217728
PASS: [hdfs getconf dfs.namenode.name.dir] -> /hadoop/dfs/name
PASS: [mapred getconf mapreduce.framework.name] -> yarn
PASS: [mapred getconf mapreduce.jobhistory.address] -> namenode:10020
PASS: [mapred getconf mapreduce.task.io.sort.mb] -> 256
PASS: [yarn getconf yarn.resourcemanager.address] -> namenode:8032
PASS: [yarn getconf yarn.nodemanager.resource.memory-mb] -> 8192
PASS: [yarn getconf yarn.scheduler.minimum-allocation-mb] -> 1024
PASS: Replication factor is 2
```

---

## 📦 제출물

- modify-config.py
- verify-config.py
- 원본 config XML
- 변경된 config XML
- README_KR.md

---

## 🧠 핵심 학습 포인트

- Docker 볼륨을 이용한 Hadoop 설정 외부화
- XML 기반 Hadoop 설정 자동 수정
- Hadoop 서비스 재시작 자동화
- 실제 Hadoop 명령을 이용한 설정 검증
- 멀티 노드 YARN 기반 MapReduce 실행 확인
