from multiprocessing import Process, Queue, Value, Lock
import time

# Push
def push(q, items):
    print("pushing items to queue:")
    for i, item in enumerate(items, start=1):
        q.put(item)
        print(f"item no: {i} {item}")

    # sentinel
    q.put(None)
    q.put(None)

# pop
def pop(q, worker_id, counter, lock):
    while True:
        item = q.get()
        if item is None:  # 종료 신호
            break
        
        with lock:
            item_no = counter.value
            counter.value += 1
            
        print(f"[worker_id]: {worker_id} item no: {item_no} {item}")
        time.sleep(0.2)

if __name__ == "__main__":
    color_list = ["red", "green", "blue", "black"]

    q = Queue()
    
    counter = Value('i', 0)
    lock = Lock()

    # 프로세스 생성
    p_push = Process(target=push, args=(q, color_list))
    p1_pop = Process(target=pop, args=(q, 1, counter, lock))
    p2_pop = Process(target=pop, args=(q, 2, counter, lock))

    # 프로세스 순서 제어
    p_push.start()
    p_push.join()
    
    p1_pop.start()
    p2_pop.start()

    # 프로세스 종료 대기
    p1_pop.join()
    p2_pop.join()