#!/bin/bash
set -e

service ssh start

if [ "$HADOOP_ROLE" = "master" ]; then
    echo "Starting Hadoop Master..."

    if [ ! -d "/hadoop/dfs/name/current" ]; then
        echo "Formatting NameNode..."
        hdfs namenode -format -force
    fi

    # NameNode
    hdfs --daemon start namenode

    # ResourceManager
    yarn --daemon start resourcemanager

    # JobHistory
    mapred --daemon start historyserver

elif [ "$HADOOP_ROLE" = "worker" ]; then
    echo "Starting Hadoop Worker..."

    # DataNode
    hdfs --daemon start datanode

    # NodeManager
    yarn --daemon start nodemanager

else
    echo "Unknown role: $HADOOP_ROLE"
    exit 1
fi

tail -f /dev/null