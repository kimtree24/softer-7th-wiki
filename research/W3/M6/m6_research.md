# Amazon Product Reviews MapReduce 프로젝트 회고 (Retrospective)

## 1. 초기 질문과 고민

### Q1. 데이터가 15GB 이상인데 DataNode를 늘리면 속도가 빨라질까?
- Hadoop은 **데이터를 블록 단위로 분산 저장**하고, Map Task를 각 DataNode에서 병렬 실행한다.
- DataNode 수 증가 → 동시에 실행 가능한 Map Task 수 증가 → 처리 시간 단축 가능
- 단, 네트워크/디스크/메모리 병목이 있으면 선형적으로 빨라지지는 않음

**결론**: DataNode 증설은 Map 단계 병렬성을 높이는 데 효과적이지만, 리소스 튜닝이 병행되어야 함

---

### Q2. MapReduce에서 실제로 오래 걸리는 작업은 무엇인가?
- Map 단계: 대용량 CSV 파싱 + key-value 생성
- Shuffle 단계: 네트워크를 통한 대량 데이터 이동
- Reduce 단계: 그룹핑 및 집계

실측 결과:
- Map input records 약 **5억 6천만 건**
- Shuffle bytes 약 **9.5GB**
- 전체 시간 중 Map 단계 비중이 가장 큼

**결론**: 이 작업에서는 Map 단계와 Shuffle 비용이 가장 컸다.

---

## 3. 데이터 업로드 과정에서의 트러블슈팅

### 문제 1. `hdfs dfs -put` 중간에 Killed / Connection refused 발생
**증상**
- 대용량 CSV 업로드 중 일부 파일만 업로드
- DataStreamer 오류 및 특정 DataNode 제외 로그 발생

**원인**
- Docker 환경에서 DataNode JVM 메모리 제한 없음
- HDFS replication 동시 수행으로 메모리 폭증

**해결**
- 초기 업로드 시 `dfs.replication=1`
- 업로드 완료 후 `hdfs dfs -setrep -R 3 /data/amazon`
- Docker `mem_limit` 설정 및 YARN 메모리 제한 추가
---

## 4. Replication 관련 이해 정리

### 질문: replication 값을 나중에 바꿔도 자동으로 복제되는가?
- `dfs.replication` (xml): **미래 파일에만 적용**
- `hdfs dfs -setrep`: **이미 존재하는 파일에 적용**

실제로:
- replication 1 → 3 변경 시
- Under-replicated blocks 증가
- DataNode 간 백그라운드 복제 수행 확인

---

## 5. YARN 장애와 메모리 튜닝

### 문제 2. MapReduce 실행 시 ResourceManager Connection Refused
**증상**
- 8032 포트 연결 실패
- MapReduce 잡 제출 불가

**원인**
- 컨테이너 재기동 이후 YARN 데몬 미기동
- 또는 OOM Killer에 의해 ResourceManager 종료

**해결**
- 전체 컨테이너 재기동
- Docker 메모리 16GB 이상 할당
- YARN/MapReduce 메모리 명시적 제한

```xml
yarn.scheduler.maximum-allocation-mb=2048
yarn.nodemanager.resource.memory-mb=2048
mapreduce.map.memory.mb=512
mapreduce.reduce.memory.mb=512
```

> Docker + Hadoop 환경에서는 메모리 제한이 없으면 반드시 장애가 발생한다.

---

## 6. InvalidResourceRequestException 해결

### 문제 3. Requested memory 1536 > maximum allowed 1024
**원인**
- Map/Reduce 메모리는 줄였으나
- ApplicationMaster(AM) 기본 메모리(1536MB)가 제한 초과

**해결**
- YARN 최대 할당 메모리를 2048MB로 상향
- 또는 AM 메모리 직접 설정

> MapReduce 잡은 Map/Reduce 외에 ApplicationMaster 자원도 고려해야 한다.

---
