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
- 작성예정

## 4. 패키지 설치 (수정 예정)

W1, W2에서 작성한 노트북을 분석한 결과 다음 라이브러리가 필요했다.
	•	pandas
	•	numpy
	•	matplotlib
	•	wordcloud
	•	jupyterlab

배운 점
	•	--no-cache-dir 옵션으로 이미지 용량 최소화
	•	분석에 필요한 라이브러리만 명시적으로 설치하는 것이 중요

⸻

## 5. 어떤 파일을 Docker Image에 담아야 했는가? (수정 예정)

처음에는 노트북만 복사했지만, 실행 중 다음 문제가 발생했다.
FileNotFoundError: data/W1/mtcars.csv

이를 통해 깨달은 점은:

노트북이 의존하는 데이터 파일도 반드시 이미지에 포함되어야 한다