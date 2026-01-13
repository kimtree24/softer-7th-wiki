#!/usr/bin/env bash
set -e

# sshd 실행
service ssh start

# Hadoop 실행 유저
su - hadoop <<'EOF'
set -e

export HADOOP_HOME=/opt/hadoop
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# (중요) namenode 포맷은 "처음 1번만"
# 영속 볼륨이라면 /hadoop/dfs/namenode/current 존재 여부로 판단 가능
if [ ! -d "/hadoop/dfs/namenode/current" ]; then
  echo "[INFO] Formatting NameNode (first run)..."
  hdfs namenode -format -force -nonInteractive
fi

echo "[INFO] Starting HDFS..."
start-dfs.sh

echo "[INFO] Starting YARN..."
start-yarn.sh

echo "[INFO] Hadoop services are up."
echo " - NameNode UI: http://localhost:9870"
echo " - YARN UI:     http://localhost:8088"

# 컨테이너 유지
tail -f /opt/hadoop/logs/*.log
EOF