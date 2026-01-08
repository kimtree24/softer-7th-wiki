# multiprocessing.Pool 정리

## 1. multiprocessing.Pool 정의
- 여러 개의 프로세스를 미리 생성해 두고 (worker pool) 여러 작업을 분산하여 병렬로 실행하기 위한 고수준(high-level) API이다.

## 2. 핵심 특징
- 스레드(thread)가 아닌 프로세스(process) 기반 병렬 처리
- CPU-bound 작업에 적합
- 프로세스 생성·종료를 Pool이 자동으로 관리
- 개발자는 “무엇을 병렬로 실행할지”에만 집중하면 됨

## 3. Pool 생성자 인자 정리

```
Pool(processes=None, initializer=None, initargs=(), maxtasksperchild=None)
```
### 1) processes
- 워커 프로세스 개수
- 기본값: os.cpu_count()
- 동시에 실행 가능한 작업 수를 결정

```
Pool(processes=4)  # 최대 4개의 작업 병렬 실행
```
### 2) initializer
- 각 워커 프로세스가 시작될 때 한 번 실행되는 함수
- 주로 DB 커넥션 초기화, 전역 변수 설정, 공통 리소스 로딩에 사용

```
def init_worker():
    print("worker init")

Pool(initializer=init_worker)
```

### 3) initargs
- initializer 함수에 전달할 인자 튜플

```
Pool(initializer=init_worker, initargs=(arg1, arg2))
```

### 4) maxtasksperchild
- 워커 프로세스 하나가 처리할 최대 작업 수
- 지정한 작업 수를 처리하면 해당 프로세스 종료 후 재생성
- 메모리 누수 방지, 장시간 실행되는 배치 안정성 확보

```
Pool(maxtasksperchild=100)
```

## 4. Pool 주요 메서드

### 1) map()

```
pool.map(func, iterable)
```

- iterable의 각 요소를 func에 전달
- 결과 순서 보장
- 모든 작업이 끝날 때까지 blocking

```
results = pool.map(square, [1, 2, 3, 4])
```

### 2) apply()

```
pool.apply(func, args)
```

- 단일 작업 실행
- 동기(blocking) 방식

```
result = pool.apply(square, (10,))
```

### 3) apply_async()

```
pool.apply_async(func, args, callback)
```

- 단일 작업 실행
- 비동기(non-blocking)
- get() 호출 시 결과 반환

```
res = pool.apply_async(square, (10,))
result = res.get()
```

### 4) imap() / imap_unordered()
- iterator 형태로 결과 반환
- 대량 데이터 처리 시 메모리 효율적

## 5. Context Manager 사용 (with Pool(...))

```
with Pool(processes=2) as pool:
    pool.map(func, data)
```

이 구문은 내부적으로 다음을 자동 처리한다.

```
pool.close()
pool.join()
```

## 6. if __name__ == "__main__" 필요한 잉ㅍ

- Windows / macOS는 spawn 방식으로 프로세스 생성
- 새로운 프로세스가 현재 파일을 다시 실행
- 보호 없이 Pool 생성 시 → 무한 프로세스 생성