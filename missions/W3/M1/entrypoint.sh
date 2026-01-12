#!/bin/bash

# docker 컨테이너를 HDFS 서버로 만드는 부팅 시퀀스

# 에러 나면 즉시 스크립트 중단 - 중간에 에러 씹히면 안되니까.
set -e

# HDFS 최초 실행이면 포맷
# 해당 디렉토리가 있다면 이미 HDFS가 포맷되어 있고, 기존 파일 시스템이 존재한다는 뜻
if [ ! -d "/hadoop/dfs/name/current" ]; then
  echo "Formatting NameNode..."
  # HDFS 파일 시스템을 생성하는 것
  # HDFS root/ , 블록 풀, 네임스페이스 생성
  hdfs namenode -format -force
fi

# SSH 데몬 / Hadoop 내부 통신
service ssh start

# HDFS 시작 / NameNode + DataNode 실행
echo "Starting HDFS..."
start-dfs.sh

# 웹 UI 로그 보기용
tail -f $HADOOP_HOME/logs/*