#!/bin/bash
service ssh start

if [ ! -d "/hadoop/dfs/name/current" ]; then
  /format.sh
fi

start-dfs.sh
start-yarn.sh

tail -f /dev/null