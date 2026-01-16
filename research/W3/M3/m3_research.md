# Hadoop MapReduce WordCount

## 1. 개념 정리

### 1.1 Hadoop Streaming
Mapper와 Reducer는 표준입출력(STDIN/STDOUT) 기반으로 동작한다. Python 스크립트에서 `print`는 곧 Hadoop으로 보내는 (key, value) 출력이며, return 값은 무시된다.

### 1.2 Docker Volume과 HDFS의 역할 분리
- ebook.txt: Docker volume으로 master 컨테이너에 주입
- HDFS: DataNode에 분산 저장
데이터와 HDFS 메타데이터를 분리 마운트해야 안정적이다.

### 1.3 NameNode, DataNode, YARN
- NameNode: 메타데이터 관리
- DataNode: 실제 블록 저장
- YARN: MapReduce 작업을 각 DataNode로 스케줄링

## 2. 아키텍처 및 네이밍 이슈

### 2.1 hostname vs container_name
Hadoop은 Docker의 container_name이 아니라 컨테이너 hostname과 core-site.xml의 fs.defaultFS를 기준으로 NameNode를 찾는다. 따라서 hostname과 fs.defaultFS는 반드시 일치해야 한다.

### 2.2 workers 파일
workers 파일에 정의된 호스트명과 Docker Compose의 hostname이 일치해야 DataNode가 정상 등록된다.