# MovieLens Hadoop MapReduce 프로젝트

## 1. 초기에 막혔던 부분들

### (1) 두 개의 입력 파일 처리
movies.csv와 ratings.csv를 동시에 입력으로 주었을 때,
Hadoop Streaming에서는 각 파일이 서로 다른 Mapper 인스턴스로 분리되어 처리된다.
이를 구분하기 위해 mapreduce_map_input_file 환경변수를 사용해 파일 이름에 따라 다른 mapper를 실행해야 했다.

### (2) Reduce-side Join 이해 부족
처음에는 movies와 ratings를 어떻게 join해야 할지 몰랐지만,
MapReduce에서는 같은 key(movieId)를 기준으로 Reducer에 모아주는 shuffle 단계가 핵심이다.

그래서 mapper에서 다음과 같은 태그를 붙였다:
- movies: M|title
- ratings: R|rating

Reducer에서는 이 태그를 기준으로 데이터를 구분해 조인하였다.

## 2. Hadoop Streaming에서 중요한 개념

### mapreduce_map_input_file
각 Mapper가 처리 중인 입력 파일의 HDFS 경로가 저장된 환경 변수이다.
이를 사용하면 하나의 Job에서 서로 다른 파일에 대해 다른 Mapper를 실행할 수 있다.

## 3. Hadoop MapReduce 처리 흐름

1. HDFS에서 데이터를 split 단위로 읽음
2. Mapper가 (key, value) 출력
3. Hadoop이 key 기준으로 정렬 및 grouping
4. Reducer가 key별로 값을 받아 집계
5. 결과를 HDFS에 저장