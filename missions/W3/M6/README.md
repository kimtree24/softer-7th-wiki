# Amazon Product Reviews MapReduce

## 1. 프로젝트 개요
본 프로젝트는 Apache Hadoop과 MapReduce에 대한 이해를 입증하기 위해 Amazon Product Reviews 2023 데이터셋을 사용하여 가장 많이 리뷰된 상품과 그 평균 평점을 계산하는 Python 기반 MapReduce 작업을 구현한 것이다.

## 2. 학습 목표 및 과제 정의
- Hadoop 클러스터(HDFS + YARN) 환경에서 대용량 데이터를 처리
- Mapper에서 (상품ID, 평점) key-value 생성
- Reducer에서 상품별 리뷰 수와 평균 평점 계산
- 결과를 HDFS에 저장 및 검증

## 3. 사용 데이터셋
- 데이터셋: Amazon Reviews 2023
- 출처: https://amazon-reviews-2023.github.io/

## 4. 시스템 아키텍처
- Docker 기반 멀티 노드 Hadoop 클러스터
- Master: NameNode, ResourceManager
- Workers: DataNode, NodeManager
- HDFS Replication Factor: 3

## 5. 데이터 업로드 절차
```bash
hdfs dfs -mkdir -p /data/amazon
for f in /data/amazon/*.csv; do
  hdfs dfs -put "$f" /data/amazon/
done
```

## 6. MapReduce 실행
```bash
hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar   -files /src/mapper.py,/src/reducer.py   -mapper "python3 mapper.py"   -reducer "python3 reducer.py"   -input /data/amazon   -output /output/amazon_product_stats
```

## 7. 결과 확인
```bash
hdfs dfs -ls /output/amazon_product_stats
hdfs dfs -cat /output/amazon_product_stats/part-00000 | head
```

출력 형식:
상품ID    리뷰수    평균평점

## 8. 결과 검증
- Map input records 약 5억 건
- Reduce output records 약 4천8백만 건
- HDFS에 약 800MB 결과 생성 확인