## **multiprocessing.Queue**

### **핵심 질문**

> multiprocessing.Queue는 왜 존재하는가?
> 

### **핵심 답변**

multiprocessing.Queue는 자료구조가 아니라 프로세스 간 통신(IPC)을 위한 통로

- 프로세스는 **메모리를 공유하지 않는다**
- list, deque는 프로세스 간 공유 불가
- Queue는 내부적으로:
    - pipe
    - lock
    - pickle
    
    을 사용해 **데이터를 복사 전달**
    

Process + Queue = 멀티프로세싱

Queue 단독 = 그냥 큐

## **deque와의 차이**

| **항목** | **multiprocessing.Queue** | **collections.deque** |
| --- | --- | --- |
| 목적 | 프로세스 간 통신 | 단일 프로세스 자료구조 |
| 멀티프로세스 안전 | O | X |
| 메모리 공유 | O (복사 전달) | O |
| 병렬 확장 | O | X |

 deque를 쓰면 **항상 하나의 프로세스가 순차 처리**

## **while q: / while not q.empty() 문제**

### 발생한 문제

```python
while q:
    item = q.get()   # 종료 안 됨
```

```python
while not q.empty():
    item = q.get()   # 처음 실행 시 pop 안 나옴
```

**이유 1.  Queue는 truth value를 지원하지 않음**

```python
bool(q)  # 항상 True
```

 while q: 는 **절대 종료 조건이 아님**

**이유 2. multiprocessing.Queue.empty() 는 신뢰 불가**

```
put()
 ↓
로컬 버퍼
 ↓
feeder thread
 ↓
OS pipe
```

- put() 직후에도
- feeder thread가 아직 IPC로 안 보냈을 수 있음
- 그래서 empty()가 **True로 나올 수 있음**

 **공식 문서에서도 empty()는 unreliable**

### **올바른 pop 패턴**

- **Sentinel 방식 (정석)**
    
    ```python
    q.put(None)
    
    while True:
        item = q.get()
        if item is None:
            break
    ```