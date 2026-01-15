# Hadoop 설정 파일

## 전체 구조 한 장 요약

- **HDFS (저장 계층)**  
  - **NameNode**: 메타데이터(파일→블록→DataNode 위치) 관리  
  - **DataNode**: 실제 블록 저장  
- **YARN (연산 리소스 계층)**  
  - **ResourceManager(RM)**: 클러스터 전체 자원 스케줄링  
  - **NodeManager(NM)**: 각 워커 노드의 자원/컨테이너 실행  
- **MapReduce (배치 연산)**  
  - YARN 위에서 컨테이너로 Mapper/Reducer 실행

설정 파일은 크게 다음처럼 나뉜다.

| 파일 | 계층 | 핵심 역할 |
|---|---|---|
| `core-site.xml` | 공통 | “클러스터를 어디로 보낼지”, 공통 IO/보안/임시경로 |
| `hdfs-site.xml` | HDFS | NameNode/DataNode 저장 위치, 복제/블록, 안전모드 등 |
| `mapred-site.xml` | MapReduce | MapReduce가 YARN 위에서 어떻게 동작하는지 |
| `yarn-site.xml` | YARN | 노드 자원량, 스케줄러, 컨테이너/로그 등 |

---

# 1) `core-site.xml` — Hadoop 공통/기본 설정

## 1.1 역할
`core-site.xml`은 Hadoop 전체에 공통으로 적용되는 “기본 토대” 설정이다.

- 기본 파일시스템(HDFS) 엔드포인트 지정 (`fs.defaultFS`)
- 공통 임시 디렉토리 지정 (`hadoop.tmp.dir`)
- 각종 Hadoop IO 버퍼/압축/프록시/보안(케르베로스) 등 공통 레벨 옵션
- (운영 환경에서) HA 구성 시 네임서비스 이름, failover 관련 설정의 기반이 되기도 함

> **실제로 가장 많이 맞닥뜨리는 문제**  
> - `fs.defaultFS`가 컨테이너 hostname/네트워크 DNS와 안 맞아서 HDFS 명령이 이상하게 동작  
> - `hadoop.tmp.dir`이 휘발성 경로라서 컨테이너 재시작 시 메타/캐시가 손실

---

## 1.2 핵심 설정 항목

### (A) `fs.defaultFS` — “HDFS를 어디로 볼 것인가”
```xml
<property>
  <name>fs.defaultFS</name>
  <value>hdfs://master:9000</value>
</property>
```

- 의미: `hdfs dfs -ls /` 같은 명령이 **기본적으로 접속할 파일시스템**
- 값 형태:
  - `hdfs://<namenode-host>:<port>`
  - HA 구성 시 `hdfs://<nameservice>` 형태

**튜닝/운영 포인트**
- Docker에서는 `<namenode-host>`가 **docker-compose service 이름** 또는 **hostname**과 DNS로 해석 가능해야 함.
- “hostname을 바꿨는데도 동작한다”는 건 보통:
  - Docker DNS가 `container_name` 또는 service 이름으로도 해석해주거나
  - `/etc/hosts`에 별칭이 들어가 있거나
  - 같은 네트워크에서 이름 해석이 우연히 맞아떨어진 경우가 많음  
→ 운영 환경에서는 **명시적으로 통일**하는 게 안전.

---

### (B) `hadoop.tmp.dir` — Hadoop 공통 임시 저장소
```xml
<property>
  <name>hadoop.tmp.dir</name>
  <value>/hadoop/tmp</value>
</property>
```

- 의미: Hadoop이 내부적으로 사용하는 임시 파일 저장 경로(각종 캐시, 소켓, 중간 데이터 등)
- 컨테이너에서 `/tmp` 같은 휘발성 공간을 쓰면 재시작 시 일부 상태가 사라질 수 있음

**튜닝/운영 포인트**
- 최소한 **퍼시스턴트 볼륨**(bind mount/volume)로 유지할지 검토  
- 로그/임시가 섞이면서 디스크가 꽉 차면 전체가 멈추기도 함 → 디스크 모니터링 중요

---

# 2) `hdfs-site.xml` — HDFS 저장 동작의 핵심 설정

## 2.1 역할
`hdfs-site.xml`은 HDFS의 “저장 정책/구조”를 결정한다.

- 블록 사이즈, 복제 수, 랙 어웨어니스(운영)
- NameNode 메타데이터 디렉토리
- DataNode 블록 저장 디렉토리
- Safe mode, 체크포인트(운영)

---

## 2.2 핵심 설정 항목

### (A) `dfs.replication` — 복제본 수(기본값)
```xml
<property>
  <name>dfs.replication</name>
  <value>2</value>
</property>
```

- 의미: 각 블록을 기본적으로 몇 개의 DataNode에 저장할지
- 주의: 파일 업로드 시 개별 파일 단위로도 replication을 바꿀 수 있음  
  - `hdfs dfs -setrep -w 3 /path/file`

**튜닝 포인트**
- 복제 수 ↑
  - 장점: 장애 허용성 증가, 읽기 성능(동시 읽기) 향상 가능
  - 단점: 저장공간 사용량 증가, 쓰기 비용/네트워크 비용 증가
- 로컬(소규모 2~3노드)에서는 `1~2`가 현실적  
- 운영(수십~수백 노드)에서는 흔히 `3`이 기본(조직/요구사항에 따라 다름)

---

### (B) `dfs.blocksize` — 블록 크기
```xml
<property>
  <name>dfs.blocksize</name>
  <value>134217728</value> <!-- 128MB -->
</property>
```

- 의미: 파일을 HDFS에 저장할 때 분할되는 “기본 블록 크기”
- 블록 크기 ↑
  - 장점: 메타데이터(블록 수) 감소, 대용량 순차 처리에 유리
  - 단점: 작은 파일이 많은 경우 비효율, 병렬성(블록 단위) 감소 가능

**튜닝 포인트**
- 대규모 배치 처리(로그/리뷰)에서 128MB~256MB로 두는 경우가 많음  
- 너무 작은 블록은 NameNode 메타데이터 부담 증가

---

### (C) NameNode 메타데이터 위치 — `dfs.namenode.name.dir`
```xml
<property>
  <name>dfs.namenode.name.dir</name>
  <value>/hadoop/dfs/name</value>
</property>
```

- 의미: NameNode의 메타데이터(FSImage, EditLog 등)가 저장되는 경로

**운영 포인트**
- Docker에서 별도 볼륨 마운트를 하는 이유: 컨테이너 재시작/재생성에도 메타데이터 유지
- 운영에선 디스크 이중화/RAID, 또는 HA 구성에서 안정성 확보

---

### (D) DataNode 데이터 위치 — `dfs.datanode.data.dir`
```xml
<property>
  <name>dfs.datanode.data.dir</name>
  <value>/hadoop/dfs/data</value>
</property>
```

- 의미: DataNode가 실제 블록 파일을 저장하는 경로
- 각 worker마다 서로 다른 로컬 디스크(또는 마운트)로 지정하는 경우가 많음

**튜닝 포인트**
- 여러 디스크를 콤마로 나열해 병렬 디스크 사용 가능
- 디스크 여유/IO 상태가 곧 HDFS 성능/안정에 직결

---

# 3) `mapred-site.xml` — MapReduce 실행 설정(Framework)

## 3.1 역할
MapReduce Job이 “어디서/어떤 프레임워크로” 실행되는지, 그리고 실행 리소스 관련 기본을 지정한다.

- `mapreduce.framework.name=yarn` : YARN 위에서 실행
- Map/Reduce Task 기본 메모리/옵션
- JobHistory 서버(완료된 작업 로그 조회)

---

## 3.2 핵심 설정 항목

### (A) `mapreduce.framework.name` — YARN 연동 여부
```xml
<property>
  <name>mapreduce.framework.name</name>
  <value>yarn</value>
</property>
```

- 의미: MapReduce를 YARN 위에서 실행

---

### (B) JobHistory 서버(작업 기록)
```xml
<property>
  <name>mapreduce.jobhistory.address</name>
  <value>master:10020</value>
</property>
```

- 의미: 완료된 Job에 대한 기록 조회(디버깅/성능 분석)

---

### (C) Map/Reduce 컨테이너 자원(대표 튜닝 포인트)
(클러스터 자원과 연동됨 — YARN 설정과 같이 봐야 함)

- `mapreduce.map.memory.mb`
- `mapreduce.reduce.memory.mb`
- `mapreduce.map.java.opts`
- `mapreduce.reduce.java.opts`

**튜닝 감**
- Task가 OOM이 나면 이 값이 낮거나, 입력 분할/병렬도가 과도한 경우
- 메모리를 올리면 “컨테이너 하나당 자원”이 늘어 동시 실행 수가 줄 수 있음(트레이드오프)

---

# 4) `yarn-site.xml` — YARN 리소스 매니지먼트(스케줄링/컨테이너)

## 4.1 역할
YARN은 “클러스터의 CPU/메모리 자원을 컨테이너 단위로 분배하는 OS 같은 존재”

`yarn-site.xml`은:
- ResourceManager 주소
- NodeManager가 보고하는 자원량
- 스케줄러 정책(FIFO/Capacity/Fair)
- 로그/로컬 디렉토리

---

## 4.2 핵심 설정 항목

### (A) `yarn.resourcemanager.hostname` — RM 위치
```xml
<property>
  <name>yarn.resourcemanager.hostname</name>
  <value>master</value>
</property>
```

- 의미: 모든 NodeManager는 이 RM에 heartbeat를 보내고 컨테이너 할당을 받음
- Docker에서 service/hostname과 불일치하면 작업이 안 뜨는 대표 원인

---

### (B) NodeManager 자원량(튜닝 포인트)
```xml
<property>
  <name>yarn.nodemanager.resource.memory-mb</name>
  <value>4096</value>
</property>
```

- 의미: “이 노드에서 YARN이 쓸 수 있는 총 메모리”
- Docker Desktop에서 호스트 메모리 제한이 걸려있다면 과하게 잡으면 컨테이너가 죽을 수 있음

보통 함께 보는 값:
- `yarn.scheduler.maximum-allocation-mb` : 컨테이너 1개 최대 메모리
- `yarn.scheduler.minimum-allocation-mb` : 컨테이너 1개 최소 메모리(할당 단위)

---

## 결론
- `core-site` = “어디로 접속할지/공통 토대”
- `hdfs-site` = “어디에 저장하고 얼마나 복제할지”
- `mapred-site` = “MapReduce가 YARN 위에서 어떻게 돌지”
- `yarn-site` = “자원을 어떻게 쪼개서 컨테이너로 배분할지”


# M4 – 키워드 기반(Predefined Keywords) 없이 감성 분류

> 목표: “좋다/나쁘다 단어 세기” 같은 **사전 키워드 방식**이 아닌 방법으로 트윗 감성을 분류하는 접근을 정리한다.  
> 전제 데이터: Sentiment140 (트윗 텍스트 + 레이블)

---

## 1. 왜 키워드 방식이 한계가 있는가?

키워드 방식은 보통 아래처럼 동작한다.

- 긍정 단어(positive lexicon) 리스트와 부정 단어(negative lexicon) 리스트를 만든다.
- 문장에 등장한 단어를 세어서 점수를 계산한다.
- 점수로 긍/부정을 결정한다.

### 한계
- **부정/반어** 처리 약함: `not good`, `hardly liked`, `yeah right...`
- **문맥**을 고려하지 못함: `good`이 등장해도 전체 의미가 부정일 수 있음
- 도메인/표현 변화에 취약: 슬랭, 신조어, 이모지, 축약어에 약함
- 키워드 사전 제작이 인력 의존(유지보수 비용)

따라서 “데이터로부터 분류 규칙을 학습”하는 방법이 필요하다.

---

# 2. TF-IDF + 머신러닝 (전통적 텍스트 분류 파이프라인)

## 2.1 핵심 아이디어(원리)
문장을 사람이 만든 키워드 규칙으로 판단하지 않고,
**텍스트를 숫자 벡터로 바꾼 다음(Feature Engineering)**  
**지도학습 분류기(Classifier)** 로 학습해 감성을 분류한다.

- TF-IDF는 “문서에서 중요한 단어”를 수치화하는 대표 기법
- 분류기는 그 수치 패턴을 학습하여 긍/부정을 구분

---

## 2.2 TF-IDF 개념

### (A) TF(Term Frequency)
특정 단어가 문서(문장)에서 얼마나 자주 등장하는지

- 예: 트윗에서 `great`가 2번 나오면 TF가 높음

### (B) IDF(Inverse Document Frequency)
모든 문서에서 흔하게 등장하는 단어는 중요도가 낮고,  
특정 문서들에서만 주로 등장하는 단어는 중요도가 높다는 아이디어

- 예: `the`, `is` 같은 단어는 어디에나 있으므로 정보량이 낮음 → IDF 낮음
- 예: `fantastic`, `awful` 같은 단어는 특정 감성에서 자주 등장 → IDF 높음

### (C) TF-IDF 점수
TF와 IDF를 곱해, “이 단어가 이 문서에서 얼마나 유의미한가”를 나타냄

> 직관:  
> - 문서 내에서 자주 나오고(TF↑)  
> - 전체 문서에서는 드물수록(IDF↑)  
> → 그 단어는 해당 문서를 설명하는 데 중요하다.

---

## 2.3 전체 프로세스(학습/추론 파이프라인)

### Step 0) 데이터 준비
- 입력: 트윗 텍스트
- 레이블: 긍정/부정(또는 3클래스)

### Step 1) 전처리(Preprocessing)
- 소문자화, URL/멘션/해시태그 처리
- 불용어 제거(선택)
- 표제어/어간 추출(선택)
- 이모지/특수문자 처리(선택)

> 여기서 “너무 과한 전처리”는 성능을 오히려 떨어뜨릴 수 있음  
> (예: 감성에 중요한 `!`, `:)` 등을 다 지우는 경우)

### Step 2) 벡터화(Vectorization)
- 각 트윗을 TF-IDF 벡터로 변환  
- 결과: (문서 수 × 단어 수) 형태의 **희소행렬(sparse matrix)**

### Step 3) 모델 학습(Training)
대표 분류기:
- **Logistic Regression**: 빠르고 튜닝 쉬움(텍스트 분류 baseline로 강력)
- **Linear SVM**: 텍스트 희소벡터에서 성능 좋은 경우 많음
- **Naive Bayes**: 빠르고 간단, baseline로 자주 사용

### Step 4) 평가(Evaluation)
- Accuracy, Precision/Recall/F1
- 불균형 데이터면 F1/ROC-AUC 고려

### Step 5) 추론(Inference)
- 새 트윗 → 동일 전처리 → TF-IDF 변환 → 분류기 예측

---

## 2.4 장점
- **키워드 사전 불필요**: 데이터로부터 분류 규칙 학습
- 구현/학습이 비교적 쉬움, 빠름
- 적은 자원으로도 강력한 baseline 가능
- 모델이 비교적 해석 가능(어떤 단어가 긍/부정에 기여했는지)

## 2.5 단점/한계
- **문맥 이해 제한**: 단어 순서/장기 의존성을 잘 못 다룸
  - `not good` 같은 부정 처리도 n-gram 없으면 어려움
- 단어가 OOV(out-of-vocabulary)면 약함(신조어, 오타, 슬랭)
- feature 차원이 커지고 희소행렬이 됨 → 메모리 부담(큰 데이터에서)

---

# 3. Word Embedding 기반 분류 (의미 기반 벡터 표현)

## 3.1 핵심 아이디어(원리)
TF-IDF는 단어를 “그냥 토큰”으로 다루고,
단어 간 의미 관계(유사도)를 반영하지 못한다.

Word Embedding은 단어를 **연속된 실수 벡터**로 표현해서  
**의미가 비슷한 단어는 벡터 공간에서 가깝게** 만든다.

- `good`, `great`, `excellent` → 서로 가까운 벡터
- `bad`, `awful`, `terrible` → 서로 가까운 벡터

이 벡터를 이용해 문장 벡터를 만들고 감성을 분류한다.

---

## 3.2 Word Embedding이란?
> 단어 → 고차원 공간의 점(벡터) 로 매핑하는 방법

### 대표 방식
- **Word2Vec**
- **GloVe**
- (더 발전된) **FastText**: subword 단위로 OOV에 강함

---

## 3.3 Word2Vec 개념 (필수 이해 포인트)

Word2Vec은 “주변 단어(문맥)로 단어 의미를 학습”한다.

### (A) CBOW (Continuous Bag of Words)
- 주변 단어들로 중심 단어를 맞추는 방식  
- 예: `I __ this movie`에서 `love`를 예측

### (B) Skip-gram
- 중심 단어로 주변 단어들을 맞추는 방식  
- 예: `love`를 보고 `I`, `this`, `movie` 등을 예측

둘 다 결과적으로 “문맥이 비슷한 단어는 벡터가 비슷해진다”를 얻는다.

---

## 3.4 GloVe 개념
GloVe는 “단어 동시 출현(co-occurrence) 통계”를 기반으로
전역적인 통계 정보를 반영해 임베딩을 학습한다.

- Word2Vec: 로컬 문맥 예측 기반
- GloVe: 전역 동시출현 행렬 기반

둘 다 실제 사용은 “학습된 단어 벡터를 가져다 쓴다”가 많다.

---

## 3.5 Word Embedding 기반 감성 분류 프로세스

### Step 0) 임베딩 준비
- 선택 1) 공개된 Pretrained 임베딩 사용
- 선택 2) Sentiment140 트윗으로 Word2Vec/GloVe 직접 학습

### Step 1) 문장(트윗) 벡터 만들기
대표 방법
1) **평균(average) 임베딩**  
   - 트윗에 있는 단어 임베딩들을 평균 내서 문장 벡터 생성  
2) **TF-IDF 가중 평균**  
   - 중요한 단어에 더 큰 가중치를 주기 위해 TF-IDF로 가중 평균
3) (고급) RNN/CNN으로 sequence를 그대로 넣기 (딥러닝 단계)

### Step 2) 분류기 학습
- 문장 벡터를 입력으로 Logistic Regression / SVM / MLP 등을 학습

---

## 3.6 장점
- 의미 유사성을 반영 → TF-IDF보다 일반화에 유리할 수 있음
- 차원이 비교적 작음(예: 100~300차원) → 모델/메모리 부담 감소
- 슬랭/표현 변화에도 어느 정도 견딤(특히 FastText)

## 3.7 단점/한계
- 단순 평균 방식은 **단어 순서/부정 구조**를 제대로 못 잡음  
  - `not good`에서 `not`과 `good` 평균은 애매해질 수 있음
- 도메인 차이:
  - 뉴스로 학습된 임베딩을 트윗에 쓰면 성능이 떨어질 수 있음
- OOV 문제:
  - pretrained에 없는 단어가 많으면 성능 하락(트윗은 특히 신조어/오타 많음)
  - FastText는 subword로 완화 가능

---

# 5. Hadoop/MapReduce 관점에서의 적용 힌트

- MapReduce는 “학습”보단 “대규모 전처리/피처 생성”에 강함  
  - 예: 토큰화, n-gram 생성, TF/DF 집계, sparse feature 만들기
- 학습은 보통:
  - Spark MLlib(분산 학습)# HDFS DataNode Replication(복제)은 어떻게 이루어지는가?

## 0) 큰 그림: HDFS는 “분산 파일 시스템”이고, Replication은 “생존 전략”이다

HDFS는 하나의 큰 파일을 여러 서버(DataNode)에 나눠 저장한다.  
이때 서버(디스크)는 **언젠가 반드시 고장난다**는 가정 하에 설계되었다.

그래서 HDFS는 기본적으로:

- 데이터를 **블록(block)** 단위로 쪼개고
- 각 블록을 여러 DataNode에 **복제(replication)** 하여 저장한다.

Replication은 “옵션”이 아니라, **HDFS의 기본 안전장치**다.

---

## 1) Replication이 왜 필요한가?

### 1.1 장애(Failure)가 기본값이기 때문
HDFS가 다루는 환경은 보통 이런 특성을 가진다.

- 노드 수가 많다(수십~수천 대)
- 일반적인 범용 서버(commodity hardware)를 사용한다
- 디스크, 네트워크, 전원 등 장애가 자주 발생한다

따라서 “어떤 노드 하나가 죽는 것”은 예외가 아니라 **일상적인 이벤트**다.

**Replication이 없으면?**
- 어떤 DataNode가 죽는 순간, 그 노드에 있던 블록은 영구 손실
- 파일의 일부 블록이 없어지면 파일 전체를 읽을 수 없게 됨(사실상 데이터 유실)

---

### 1.2 가용성(Availability)을 높인다
복제본이 여러 곳에 있으면, 어떤 노드가 죽어도 다른 복제본으로 읽을 수 있다.

- 장애 발생해도 서비스 지속
- 운영자가 수동 복구하지 않아도 시스템이 자동으로 견딤

---

### 1.3 읽기 성능(Read Throughput)을 높일 수 있다
읽기 요청이 많을 때:

- 클라이언트는 여러 복제본 중 가까운(또는 여유 있는) DataNode에서 읽을 수 있음
- 병렬 읽기(large scan)에서 처리량이 개선될 수 있음

> 단, “쓰기 성능”은 복제 수가 늘수록 비용이 증가한다(네트워크/디스크).

---

## 2) “어느 레벨”에서 replication이 이루어지는가?

핵심: **HDFS replication은 “파일 전체”가 아니라 “블록(block) 단위”로 이루어진다.**

### 2.1 블록(Block) 단위 복제
HDFS는 파일을 기본 블록 크기(예: 128MB)로 나눈다.

- 파일 F = [B1, B2, B3, ...]
- replication factor = 3 이면
  - B1이 3개 DataNode에 저장
  - B2도 3개 DataNode에 저장
  - ...

즉, 복제는 다음처럼 동작한다.

```
F.txt
 ├─ Block B1 → DN2, DN5, DN9
 ├─ Block B2 → DN1, DN3, DN8
 └─ Block B3 → DN4, DN6, DN7
```

### 2.2 “DataNode replication”이라는 말의 정확한 의미
일반적으로 “datanode replication”이라고 말하지만,
정확히는 **DataNode 자체가 복제되는 게 아니라**, DataNode들에 **블록이 복제되어 저장**된다.

- DataNode는 저장소/서버 역할
- 복제되는 대상은 “블록 데이터”

---

## 3) “쓰기(write)” 시 replication은 어떻게 만들어지는가? (파이프라인)

HDFS에서 파일을 쓰면, 클라이언트는 NameNode와 DataNode를 함께 사용한다.

### 3.1 단계별 흐름

#### Step 1) 클라이언트가 NameNode에 “어디에 쓸지” 물어본다
- “이 블록(B1)을 저장할 DataNode 후보 3개를 달라”
- NameNode는 “블록 배치 정책(placement policy)”에 따라 DN 리스트를 반환한다.

예:
```
[DN2, DN5, DN9]
```

#### Step 2) 클라이언트는 첫 번째 DataNode에 데이터를 전송한다
- 클라이언트 → DN2 로 전송

#### Step 3) DataNode들끼리 파이프라인으로 복제한다
- DN2는 데이터를 받으면서 동시에 DN5로 전달
- DN5는 받으면서 동시에 DN9로 전달

즉, 복제는 **동시에 스트리밍**으로 진행된다.

```
Client → DN2 → DN5 → DN9
```

#### Step 4) ACK(확인 응답)가 역방향으로 올라온다
- DN9 저장 완료 → DN5 → DN2 → Client
- replication factor만큼 **모든 복제본이 성공해야** 해당 패킷/블록이 성공 처리된다.

---

## 4) NameNode는 replication을 어떻게 “추적”하는가?

NameNode는 실제 데이터를 저장하지 않는다.  
대신 “메타데이터”로 아래를 관리한다.

- 파일 → 블록 목록
- 각 블록 → 어느 DataNode에 존재하는지(위치 정보)
- 각 DataNode의 상태(살아있는지, 용량, 스토리지 등)

### 4.1 Heartbeat (생존 신호)
DataNode는 주기적으로 NameNode에게 heartbeat를 보낸다.

- heartbeat가 일정 시간 이상 끊기면
  - NameNode는 해당 DataNode를 **dead**로 판단한다.

### 4.2 Block Report (보유 블록 보고)
DataNode는 자신이 가진 블록 목록을 NameNode에 보고한다.

- NameNode는 이를 통해 “각 블록의 복제본 수”를 계산한다.

---

## 5) DataNode가 죽으면 replication은 어떻게 복구되는가? (Re-replication)

DataNode가 다운되면, 그 노드에 있던 블록 복제본은 사라진다.
NameNode는 이를 감지하고 **복제 수를 다시 맞추는 작업**을 자동 수행한다.

### 5.1 Under-Replicated Blocks
예를 들어 replication=3인데,
어떤 블록 B1이 DN2가 죽어서 2개만 남으면:

- B1은 under-replicated 상태가 된다.

### 5.2 Re-replication 절차
1. NameNode가 “복제 부족 블록 목록”을 만든다
2. 살아있는 복제본을 가진 DataNode를 소스(source)로 선택한다
3. 새로 복제본을 저장할 타겟(target) DataNode를 선택한다
4. 소스 DN → 타겟 DN 으로 블록 복사를 수행한다
5. 복제본 수가 다시 replication factor에 도달하면 정상 상태로 복귀한다

> 이 과정은 운영자가 수동으로 하지 않아도 자동으로 수행된다.

---

## 6) 블록 배치 정책(Placement Policy) – 복제본을 “어디에” 둘 것인가?

HDFS는 단순히 “아무 노드 3개”에 저장하지 않는다.  
목표는 다음 2가지를 동시에 만족하는 것이다.

- 장애에 강할 것(특정 장애로 한꺼번에 사라지지 않게)
- 읽기/쓰기 성능이 좋을 것(네트워크 비용 최소화)

### 6.1 랙(Rack) 인지 복제 (Rack Awareness)
운영 환경에서는 서버들이 랙 단위로 묶인다.
랙 스위치가 죽거나 랙 전원이 나가면 랙 전체가 날아갈 수 있다.

그래서 HDFS는 보통:

- 복제본 일부는 **다른 랙**에 저장하도록 정책을 둔다.

---

## 7) Replication은 “무조건 많을수록 좋은가?”

아니다. replication은 **트레이드오프**다.

### 7.1 복제 수를 늘리면 좋은 점
- 장애 허용성↑ (한 노드 죽어도 안전)
- 읽기 분산↑ (여러 복제본에서 읽을 수 있음)

### 7.2 복제 수를 늘리면 나쁜 점
- 저장 비용↑ (replication=3이면 원본 대비 3배 저장)
- 쓰기 비용↑ (네트워크/디스크 IO 증가)
- 재복제(re-replication) 시 네트워크 비용↑

### 7.3 실무에서 흔한 선택
- 대규모 운영: `3`이 흔한 기본값(조직 정책에 따라 다름)
- 소규모/실습(노드 적음): `1~2`가 현실적
  - 노드가 2대인데 replication=3이면 애초에 만족 불가능

---

  - 혹은 전처리 결과를 샘플링/다운로드 후 로컬/단일 서버 학습

---

# YARN에서 task1, task2, task3 병렬 실행 전략

## 1. 기본 전제

| 구분 | 구조 |
|------|------|
| 분산 클러스터 | 10대 서버 + YARN |
| 단일 서버 | 1대 고성능 서버, Hadoop 미사용 |

---

## 2. Hadoop/YARN이 10대를 선호하는 이유

### (1) 데이터 지역성
HDFS는 데이터를 여러 DataNode에 분산 저장한다.  
YARN은 데이터가 있는 노드에서 task를 실행한다.  
→ 디스크와 네트워크를 병렬로 사용 가능

### (2) 디스크 병렬성
10대 클러스터 = 디스크 10개  
1대 서버 = 디스크 1개  
→ IO 병목에서 큰 차이가 발생

### (3) 네트워크 병렬성
Shuffle 단계에서 여러 노드가 동시에 데이터 전송  
→ 단일 서버보다 훨씬 높은 처리량

### (4) 장애 허용성
한 노드가 죽어도 나머지 노드에서 재실행 가능  
단일 서버는 죽으면 전체 작업 중단

---

## 3. 언제 단일 서버가 더 좋은가?

데이터가 작을 경우 (수 GB ~ 수십 GB):
- 네트워크 없음
- HDFS 오버헤드 없음
- YARN 스케줄링 없음
→ 단일 서버가 빠름

데이터가 커질수록 (수 TB 이상):
→ 분산 클러스터가 압도적으로 유리


# (5) Master가 망가졌을 때 “Manager”는 어떻게 아는가? (Hadoop 아키텍처 관점)

## 1) 한 장 요약: “Heartbeat + Timeout + HA(리더 선출)”로 감지한다

Hadoop 분산 아키텍처는 기본적으로 **심장박동(Heartbeat)** 과 **타임아웃**으로 장애를 감지한다.

- **(정상)** 워커 → 마스터: 주기적으로 heartbeat 전송  
- **(장애)** heartbeat가 끊기면 “상대가 죽었다/네트워크 단절”로 판단  
- **(HA 구성)** Zookeeper 기반 리더 선출/상태 감시로 Active 전환

다만 질문은 “Master가 망가졌을 때”이므로 방향이 반대다:
- 워커가 마스터로 heartbeat를 보내려다가 **연결 실패**를 겪고,
- HA가 있으면 **Standby가 Active로 승격**되며,
- 외부 운영 도구는 **프로세스/포트/HTTP healthcheck 실패**로 감지한다.

---

## 2) HDFS 관점: NameNode가 죽으면 어떻게 감지되는가?

### 2.1 (Single NameNode) — HA가 없을 때
- DataNode는 원래 NameNode로 heartbeat와 block report를 보낸다.
- NameNode가 죽으면:
  - DataNode는 **NameNode에 연결할 수 없음**
  - 클라이언트는 HDFS RPC 요청이 실패(예: “Connection refused”, “Call to … failed”)
- **결과**: 메타데이터 서버가 없으므로 HDFS의 “제어면(Control plane)”이 사라져,  
  대부분의 작업(쓰기/메타 조회)이 중단된다.

**핵심**
- 이 경우 “Hadoop 내부에서 자동 복구”는 거의 불가능 (단일 NN은 SPOF)
- 감지는 “연결 실패(타임아웃)”와 “웹 UI/포트 다운” 형태로 나타난다.

---

### 2.2 (NameNode HA 구성) — Active/Standby가 있을 때
운영 환경에서는 NameNode를 HA로 둔다.

**구성 요소**
- Active NN / Standby NN
- 공유 edit log(보통 **JournalNode** 3대 이상) 또는 NFS
- **Zookeeper + ZKFC(ZooKeeper Failover Controller)**

**감지/전환 흐름(아키텍처 시나리오)**
1. **ZKFC**는 각 NameNode의 상태를 로컬에서 감시한다(프로세스/헬스체크).
2. ZKFC는 Zookeeper에 “내 NameNode가 Active가 될 수 있음”을 등록한다.
3. Active NN이 죽거나 헬스체크 실패하면:
   - ZKFC가 Zookeeper 락(리더십)을 잃거나,
   - Standby 측 ZKFC가 새로운 리더십을 획득한다.
4. Standby NN이 **Active로 승격(failover)** 된다.
5. 새 Active NN이 서비스(클라이언트 RPC, Web UI)를 받기 시작한다.

**왜 가능한가?**
- Standby도 JournalNode의 edit log를 따라가며 **메타데이터를 계속 동기화**해두기 때문.

**중요한 운영 포인트: Fencing**
- split-brain(두 NN이 동시에 Active)을 막기 위해 fencing(강제 차단)을 수행한다.
- 예: SSH fencing, power fencing, shared storage 접근 차단 등

---

## 3) YARN 관점: ResourceManager가 죽으면 어떻게 감지되는가?

### 3.1 (Single ResourceManager) — HA가 없을 때
YARN에서 RM은 “스케줄러/조정자”이다.

- NodeManager는 주기적으로 RM에 heartbeat를 보낸다.
- RM이 죽으면 NodeManager는:
  - RM에 연결 실패
  - 일정 시간 재시도
- 실행 중이던 컨테이너는 **설정에 따라** 계속 돌 수 있지만,
  - 새 컨테이너 할당/스케줄링은 중단
  - 애플리케이션 상태 추적이 꼬이거나 재시작될 수 있음

즉,
- “현재 돌고 있던 작업” 일부는 잠깐 살아있을 수 있으나
- 클러스터는 “새 작업 배치/관리”를 못 하게 된다.

---

### 3.2 (ResourceManager HA) — Active/Standby가 있을 때
운영에서는 RM도 HA로 두는 경우가 많다.

**구성 요소**
- Active RM / Standby RM
- Zookeeper(리더 선출/상태 저장)
- (선택) Timeline Service, State Store(상태 복구 강화)

**감지/전환 흐름**
1. 각 RM은 Zookeeper를 통해 Active/Standby를 결정한다(리더 선출).
2. Active RM이 장애 나면:
   - Zookeeper 세션이 끊기거나 헬스체크 실패
3. Standby RM이 Active로 승격
4. NodeManager들은 재시도 로직으로 새 Active RM에 붙는다
5. 스케줄링/할당 재개

---

## 4) “Manager가 어떻게 알 수 있나?”를 아키텍처 관점으로 분해하면

### 4.1 Hadoop 내부에서의 감지 주체(대표)
- **ZKFC (HDFS HA)**: NameNode 프로세스/헬스 감시 + ZK 기반 failover
- **Zookeeper (HDFS/YARN HA)**: 리더 선출/세션 기반 장애 감지(세션 끊김 = 장애 신호)
- **NodeManager/DataNode 자체**: 마스터로의 연결 실패를 통해 간접적으로 장애를 체감
- **클라이언트/Job 제출자**: RPC 실패/타임아웃으로 즉시 감지

### 4.2 감지 신호의 형태(대표)
- TCP 연결 실패(Conn refused/timeout)
- RPC 예외(리모트 호출 실패)
- Web UI(9870/8088 등) 접속 실패
- Heartbeat/세션 끊김(HA)

---
