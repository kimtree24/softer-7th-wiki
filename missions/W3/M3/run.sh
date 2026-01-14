#!/bin/bash

hdfs dfs -rm -r -f /wordcount/output

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input /wordcount/input \
  -output /wordcount/output \
  -mapper src/mapper.py \
  -reducer src/reducer.py \
  -file src/mapper.py \
  -file src/reducer.py