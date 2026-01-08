# EC2 User-data 구성 & OS 선택 기준 정리

## 1. User-data

User-data는 EC2 인스턴스가 최초 생성 및 부팅 시 자동으로 실행되는 초기화 스크립트
- EC2가 처음 켜질 때
- root 권한으로
- 단 한 번 실행됨

사람이 직접 SSH로 접속해 설정해야 할 작업을 서버 생성 시점에 자동화하기 위한 장치.

## 2. User-data를 사용하는 이유

### 2.1 자동화 & 재현성
- 매번 수동으로 Docker를 설치하지 않아도 됨
- 모든 EC2 인스턴스가 동일한 환경을 가짐 

### 2.2 인프라를 코드로 관리 (IaC)
- 인프라 설정을 스크립트로 관리
- 서버 설정 자체가 문서이자 코드가 됨

## 3. OS 선택 기준

### 3.1 Amazon Linux 2의 장점
- AWS가 직접 관리하는 배포판
- AWS 서비스와의 호환성 및 안정성 우수
- Docker, ECR, EC2와의 연동이 쉬움

# Docker

## 1. Docker Image
- 로컬 환경에 의존하지 않고 동일한 실행 환경을 보장하며 EC2 위에서 바로 실행 가능한 형태
- 분석 환경 + 코드 + 데이터까지 포함한 하나의 패키지 

## 2. Docker Desktop vs Dockerfile
### 2.1 Docker Desktop
- Docker Engine을 로컬에서 실행해주는 도구
- 이미지 build / 컨테이너 run을 가능하게 함

### 2.2 Dockerfile
- 이미지를 어떻게 만들지 정의한 설계도

Docker Desktop은 도구이고, Dockerfile은 설계도이며, docker build 명령으로 실제 이미지를 생성한다.

## 3. OS Base Image 선택 과정
### 3.1 후보군 검토
- ubuntu:20.04
- python:3.10
- python:3.10-slim
- jupyter/base-notebook

### 3.2 선택 기준
- ubuntu 계열은 Python 및 패키지를 직접 설치해야 하며 이미지 크기가 큼
- jupyter/base-notebook은 편리하지만 이미지 크기가 과도하게 큼
- python:3.10은 안정적이나 불필요한 구성 요소가 포함됨

### 3.3 최종 선택 - python:3.10-slim
- Python 실행 환경이 이미 구성되어 있고 slim 버전으로 불필요한 패키지가 제거되어 이미지 크기가 작음
- 필요한 라이브러리만 명시적으로 설치 가능
- 필요한 것만 얹어 쓰는 이미지 라는 Docker 철학에 가장 부합

## 4. 패키지 설치
- pip install --no-cache-dir 옵션을 사용하면 pip 캐시가 이미지에 남지 않아 용량을 크게 줄일 수 있음
- 불필요한 패키지를 줄이는 것이 곧 이미지 최적화로 이어짐. 따라서 실제로 import한 패키지만 명시하여 설치

⸻

## 5. 어떤 파일을 Docker Image에 담아야 했는가?
### 5.1 초기 문제 상황
- 초기에는 Jupyter Notebook 파일만 Docker Image에 포함
	```
	FileNotFoundError: data/W1/mtcars.csv
	```
### 5.2 문제 원인 분석
- 노트북은 단독으로 실행되는 코드가 아니라 외부 데이터 파일에 의존하는 실행 단위
- Docker 컨테이너 내부에는 해당 데이터 파일이 존재하지 않았음

### 5.3 해결 방법

노트북이 참조하는 데이터 디렉토리 전체를 Docker Image에 포함

```
COPY data ./data
```

### 소결
- Docker Image는 코드 + 데이터 + 실행 환경을 함께 묶는 단위