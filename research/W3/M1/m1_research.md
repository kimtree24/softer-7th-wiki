# 🐘 Hadoop on Docker – 단일 노드 HDFS 아키텍처 이해

## 1. 이 실습의 본질

이번 과제는 단순히 Hadoop을 설치하는 것이 아니라,

> **“Docker 위에서 실행되는 분산 파일 시스템(HDFS)을 서비스 형태로 구축하는 것”**

이다.

즉, 우리는:
- Hadoop을 컨테이너 안에서 실행하고
- HDFS를 네트워크 서버처럼 띄우고
- 데이터는 호스트 디스크에 영속적으로 저장하는 구조를 만든다.

---

## 2. HDFS는 어디에 존재하는가?

HDFS(NameNode, DataNode)는 **Docker 컨테이너 안에서 실행**된다.  
하지만 HDFS가 사용하는 디스크는 **호스트 머신의 디스크**에 연결된다.

이 구조를 가능하게 하는 것이 **Docker Volume(Bind Mount)** 이다.

| 관점 | 위치 |
|------|------|
| HDFS 프로세스 | Docker 컨테이너 |
| HDFS 논리적 경로 (/hadoop/dfs) | 컨테이너 |
| 실제 데이터 저장 | 호스트 디스크 |

즉:

> **HDFS는 컨테이너 안에 있고, 데이터는 로컬 컴퓨터 디스크에 저장된다.**

---

## 3. 단일 노드 Hadoop이란?

단일 노드 Hadoop이란:

> NameNode + DataNode가 **하나의 서버(컨테이너)** 안에 존재하는 Hadoop 클러스터

이다.

구성:

| 역할 | 실행 위치 |
|------|---------|
| NameNode | 컨테이너 |
| DataNode | 컨테이너 |
| SecondaryNameNode | 컨테이너 |

논리적으로는 분산 구조이지만, 물리적으로는 1대 서버에 존재한다.

---

## 4. Hadoop은 왜 SSH를 사용하는가?

Hadoop은 원래:
> 수십~수백 대 서버에 동시에 명령을 내리는 분산 시스템

이기 때문에, 노드 간 통신을 **SSH**로 한다.

단일 노드에서도:
- NameNode → localhost → DataNode
형태로 SSH 접속을 사용한다.

그래서 컨테이너 내부에는:
- SSH 서버(sshd)
- 공개키 인증
이 반드시 필요하다.

---

## 5. start-dfs.sh는 무엇인가?

`start-dfs.sh`는 Hadoop이 제공하는 공식 HDFS 부팅 스크립트다.

역할:
1. NameNode 실행
2. SecondaryNameNode 실행
3. 모든 DataNode에 SSH 접속해서 DataNode 실행

즉:
> start-dfs.sh = HDFS 클러스터 전체를 부팅하는 오케스트레이터

---

## 6. ENTRYPOINT의 의미

Docker에서 ENTRYPOINT는:

> “이 컨테이너가 실행될 때 무엇을 할 것인가”를 정의

여기서는:
> 이 컨테이너를 **HDFS 서버로 부팅**하도록 설정했다.

즉:
- 컨테이너 시작
- HDFS 포맷 여부 확인
- NameNode + DataNode 실행
- 서버 유지

라는 서버 부팅 시퀀스를 담당한다.

---

## 7. NameNode 포맷이 필요한 이유

HDFS는 일반 파일시스템처럼 먼저 초기화가 필요하다.

`hdfs namenode -format`은:
> HDFS 파일시스템을 생성하는 작업

Linux의 `mkfs`와 같은 개념이다.

이미 포맷된 경우 다시 포맷하면 모든 데이터가 날아가므로,
**기존 메타데이터 디렉토리가 있는지 검사 후 1회만 실행**해야 한다.

---

## 8. fs.defaultFS의 의미

Hadoop의 핵심 설정:

> `fs.defaultFS = hdfs://localhost:9000`

이 한 줄은:

> “이 Hadoop에서 기본 파일시스템은 로컬 디스크가 아니라  
> localhost:9000에 있는 HDFS 서버다”

라는 선언이다.

이게 없으면 Hadoop은 HDFS를 쓰지 않고 로컬 파일시스템을 사용한다.

---

## 9. 9000번 포트와 9870번 포트

HDFS는 두 개의 네트워크 인터페이스를 가진다.

| 포트 | 역할 |
|------|------|
| 9000 | HDFS API (클라이언트 ↔ NameNode) |
| 9870 | HDFS 웹 UI (브라우저용) |

9000 → 프로그램이 사용하는 HDFS  
9870 → 사람이 보는 관리 화면

---

## 10. HDFS 데이터 영속성 구조

HDFS는 내부적으로 다음 두 디렉토리를 사용한다.

| 경로 | 의미 |
|------|------|
| /hadoop/dfs/name | NameNode 메타데이터 |
| /hadoop/dfs/data | DataNode 실제 블록 |

이 경로들을 Docker volume으로 호스트에 연결하면:

> 컨테이너를 삭제해도 HDFS 데이터는 유지된다.

---

## 11. 이 구조의 본질

이 실습은 단순 Docker 실습이 아니라:

> **“컨테이너 기반 분산 스토리지 서버(HDFS) 구축”**

이다.

구조적으로:
HDFS (NameNode, DataNode)
↓
Docker Container
↓
Docker Volume
↓
Host Disk

이라는 **실제 운영 서버와 동일한 구조**를 갖는다.

---

## 12. 한 줄 요약

> Docker 위에 Hadoop을 올린 것이 아니라,  
> **Docker 위에 HDFS 스토리지 서버를 띄운 것이다.**

# 260112 — Hadoop & YARN 아키텍처 이해

> **지적 정직(Intellectual Honesty)**  
> “어떤 상황에서, 어떤 문제가 있었고, 그래서 왜 이런 극단적인 선택을 했는가?”

Hadoop과 Spark는 “좋은 설계”라기보다  
**극단적인 현실 제약 속에서 살아남기 위한 선택**의 결과다.

---

## 1. Hadoop이 등장한 현실

Google, Yahoo, Facebook이 처음 맞닥뜨린 현실:

- 데이터는 **폭발적으로 증가**
- CPU는 **느리고 비싸고**
- 대용량 서버는 **매우 비쌈**
- 디스크와 네트워크는 **병목**

그래서 질문이 생김:

> **“데이터가 더럽게 많고, 컴퓨팅이 더럽게 느릴 때, 우리는 무엇을 해야 하는가?”**

대답:

> **“비싼 서버 말고, 싸고 많은 서버로 나눠서 저장하고 계산하자.”**

이것이 Hadoop의 출발점이다.

---

## 2. Hadoop의 철학

Hadoop은 세 가지 전제를 깔고 시작했다.

### 2.1 Cheap Hardware
- 고가 서버 ❌
- 고장나도 괜찮은 싼 서버 여러 대 ✅

→ 장애는 기본값(Failure is normal)

---

### 2.2 Write Once, Read Many
HDFS는 **파일을 수정하지 않는다**.

- 한 번 쓰면(write)
- 여러 번 읽는다(read)

이 극단적 가정 덕분에:

| 버리는 것 | 얻는 것 |
|--------|--------|
| 수정 | 성능 |
| 인덱스 | 단순성 |
| 동기화 | 대용량 처리 |

이것이 **Simple Coherency Model**이다.

---

### 2.3 Moving Computation is Cheaper than Moving Data

> **데이터를 옮기지 말고, 계산을 옮겨라**

데이터 100GB를 네트워크로 옮기는 것보다  
그 데이터가 있는 서버에서 연산해서 결과만 보내는 것이 훨씬 싸다.

이것이 **Hadoop의 핵심 철학**이다.

---

## 3. HDFS의 구조

HDFS는 두 가지 노드로 구성된다.

| 구성요소 | 역할 |
|--------|------|
| NameNode | “파일이 어디에 있는지”를 기억 |
| DataNode | 실제 데이터(블록)를 저장 |

### 3.1 NameNode
- 메타데이터 관리
- 블록 위치
- 파일 트리 구조

NameNode는 데이터를 직접 저장하지 않는다.

---

### 3.2 DataNode
- 실제 데이터 블록 저장
- 클라이언트와 직접 통신
- replication 수행

---

### 3.3 Fault Tolerance (장애 허용)

서버는 망가진다. 그래서:

- 데이터를 여러 DataNode에 복제(replication)
- NameNode가 “어디에 몇 개 있는지” 추적

---

## 4. Rack 개념

Rack = 물리적으로 가까운 서버 묶음

| 위치 | 네트워크 비용 |
|------|----------------|
| Same Node | 매우 빠름 |
| Same Rack | 빠름 |
| Different Rack | 매우 느림 |

Hadoop은 항상:
> **“같은 노드 → 같은 랙 → 다른 랙” 순으로 작업 배치**

---

## 5. Data Locality

Data Locality란:

> **데이터가 있는 곳에서 계산이 실행되는 것**

Hadoop이 task를 배치할 때:
- 데이터가 있는 DataNode에 task를 보내려고 한다
- 네트워크 전송을 피하기 위함

이게 안 되면:
- Rack Local
- 그래도 안 되면 Different Rack

→ 비용 폭증

---

## 6. YARN: Hadoop의 운영체제

HDFS가 **스토리지**라면  
YARN은 **클러스터 OS**다.

---

### 6.1 YARN 전체 흐름

```
Client
↓
ResourceManager
↓
ApplicationMaster 생성
↓
ApplicationMaster → RM에게 컨테이너 요청
↓
NodeManager들 중에서 컨테이너 할당
↓
Task 실행
↓
결과를 AM에게 보고
```

---

### 6.2 ResourceManager (RM)
- 클러스터 전체 자원 관리
- 어디에 어떤 App을 실행할지 결정

---

### 6.3 NodeManager (NM)
- 각 노드의 상태 관리
- CPU, 메모리, 컨테이너 실행
- RM에게 “나는 지금 얼마 남아 있음” 보고

---

### 6.4 ApplicationMaster (AM)
- 하나의 Application(MapReduce Job)의 관리자
- Task 요청
- 실패한 Task 재시작
- 진행률 관리

---

### 6.5 ApplicationManager
- AM을 생성하고
- 죽었는지 감시하고
- 재시작 관리

(AM과 다른 개념)

---

## 7. YARN과 Data Locality

RM이 컨테이너를 배치할 때 고려하는 것:

> “이 Task가 필요한 데이터는 어느 DataNode에 있는가?”

그래서:
- 가능한 한 데이터가 있는 노드에 컨테이너를 생성
- 네트워크 비용 최소화

---

## 8. MapReduce의 구조

MapReduce는:
> “데이터를 쪼개서 처리하고, 다시 합치는 모델”

### 8.1 Mapper
- stdin으로 데이터 받음
- 판단만 수행
- key-value 출력

### 8.2 Reducer
- Mapper 결과를 받아 집계

---

## 9. MapReduce와 HDFS의 관계

MapReduce는:
- 입력은 HDFS에서 읽음
- 출력은 HDFS로 씀
- **중간 결과는 로컬 디스크에 저장**

왜?
> HDFS는 write-once이기 때문에  
> shuffle 과정에서 계속 수정 불가능

---

## 10. Shuffle의 비용

Shuffle은:
> Mapper 결과를 Reducer에게 보내는 네트워크 이동

- Rack을 넘어가면 매우 느림
- 그래서 Data Locality가 매우 중요

---

## 11. 핵심 요약

Hadoop은 다음 극단적인 선택의 집합이다:

| 현실 | Hadoop의 선택 |
|------|----------------|
| 서버는 고장난다 | Replication |
| 네트워크는 느리다 | Data Locality |
| 디스크는 싸다 | Write Once |
| 서버는 싸야 한다 | Cheap Hardware |
| 데이터는 크다 | 분산 저장 |

> Hadoop은 “완벽한 시스템”이 아니라  
> **“망가져도 계속 돌아가게 만든 시스템”**이다.