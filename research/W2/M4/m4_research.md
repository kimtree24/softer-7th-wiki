# **Queue.get_nowait() & Exception Handling 정리**

## **1. get_nowait()란?**

Queue.get_nowait()는 큐에서 아이템을 **즉시(non-blocking)** 가져오는 메서드다.

- 아이템이 있으면: 즉시 반환
- 아이템이 없으면: 기다리지 않고 **예외(Empty)**를 발생

즉, get()과 달리 **대기(blocking)** 하지 않는다.

## **2. get() vs get_nowait() 차이**

| **구분** | get() | get_nowait() |
| --- | --- | --- |
| 동작 | 기본적으로 **blocking** | **non-blocking** |
| 큐가 비었을 때 | 아이템이 올 때까지 기다림 | 즉시 예외 발생 |
| 종료 처리 | sentinel 등 별도 설계 필요 | Empty 예외로 “없음” 감지 가능 |
| 대표 사용처 | producer/consumer, 안정적 종료 | 작업 큐가 “완성된 상태”일 때 빠르게 소진 |

## **3. 예외 타입: Empty**

get_nowait()에서 큐가 비면 Empty 예외가 발생한다.

주의: Empty는 다음 모듈에서 가져오는 게 일반적이다.

```python
from queue import Empty
```

- multiprocessing.Queue도 내부적으로 queue.Empty와 호환되는 예외를 던지는 형태로 쓰는 게 일반적이다.

## **4. q.empty() 를 종료 조건으로 쓰면 위험한 이유**

멀티프로세스 환경에서 empty()는 다음을 100% 보장하지 못한다.

- “지금 비었음”인지
- “곧 다른 프로세스가 넣을 예정”인지
- “내가 확인한 직후 다른 프로세스가 꺼내갈지”

즉, 아래 코드는 레이스 컨디션(경쟁 상태)이 생길 수 있다.

```python
while not q.empty():
    item = q.get()  # empty() 확인 직후 비어버리면 block 가능
```

그래서 get_nowait() + Empty 처리가 실전에서 자주 쓰인다.

## **5. multiprocessing 작업 분배에서 get_nowait()가 좋은 이유**

multiprocessing.Queue를 “작업 큐”로 쓰면, 여러 워커가 동시에 아래를 실행한다.

```python
task = tasks_to_accomplish.get_nowait()
```

- 작업이 남아 있으면: 워커가 하나 가져가 처리
- 작업이 없으면: Empty → 워커 종료

이 방식은 워커들이 작업을 **동적으로 분배**받게 해준다.

## **6. get_nowait() 방식의 한계**

get_nowait() + Empty만으로 “작업 종료”를 판단하는 방식은 작업 생산(put)이 이미 끝났다는 가정

- producer가 아직 put()을 하고 있는 중인데 consumer가 먼저 get_nowait() 했을 때 empty가 떠버리면 consumer는 “작업 끝”으로 오해하고 종료할 수 있음
    
    즉, 아래 상황에서 위험해질 수 있다:
    
    - Producer와 Consumer가 동시에 동작
    - Producer가 느리게 작업을 넣는 구조
    - 네트워크/IO로 작업 생성이 지연되는 구조

 이런 경우에는 **sentinel** 또는 **Event** 같은 명시적인 종료 신호가 필요하다.

## **7. get_nowait() vs sentinel 언제 쓰나?**

### **get_nowait()가 잘 맞는 경우**

- 작업이 **미리 큐에 다 채워져 있음**
- “큐가 비면 종료”가 자연스러움
- 워커 수가 많고 단순 분배가 목적

예: 미리 준비된 10개 Task를 4개 워커가 처리

### **sentinel이 잘 맞는 경우**

- Producer/Consumer가 동시에 동작
- “작업 끝”을 확실하게 전달해야 함
- 워커가 block 상태에서 안전하게 종료되어야 함

예: 실시간 스트림 처리, 로그 소비, 지속적으로 작업이 들어오는 구조