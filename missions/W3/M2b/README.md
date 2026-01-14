# W3 M2b – Hadoop Multi-Node Cluster 설정 자동화 & 검증

## 시스템 구조

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

## 설정 변경 대상

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

## 실행 방법

### 클러스터 초기 실행

```bash
docker-compose up -d
```

---

### 설정 변경 실행

```bash
python3 modify-config.py ./config
```

수행 작업:
- `config_backup/`에 기존 XML 백업
- XML 값 수정
- Hadoop 서비스 재시작 (stop-dfs, stop-yarn → start-dfs, start-yarn)

---

### 설정 검증 실행

```bash
python3 verify-config.py
```

확인 내용:
- hdfs getconf / mapred getconf / yarn getconf 값 비교
- HDFS 테스트 파일 생성
- 복제 계수 확인
- MapReduce WordCount 실행 (YARN 사용 여부)
- ResourceManager 메모리 설정 확인
