#!/bin/bash
set -e

service ssh start

if [ "$HADOOP_ROLE" = "master" ]; then
    echo "Starting Hadoop Master..."
    
    if [ ! -d "/hadoop/dfs/name/current" ]; then
        echo "Formatting NameNode..."
        hdfs namenode -format -force
    fi

    start-dfs.sh
    start-yarn.sh

elif [ "$HADOOP_ROLE" = "worker" ]; then
    echo "Starting Hadoop Worker..."

    hdfs --daemon start datanode
    yarn --daemon start nodemanager
else
    echo "Unknown role: $HADOOP_ROLE"
    exit 1
fi

tail -f /dev/null