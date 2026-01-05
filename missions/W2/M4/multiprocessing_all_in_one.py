from multiprocessing import Process, Queue, current_process
from queue import Empty
import time

# 각 프로세스가 수행할 작업 함수
def worker(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            # 작업 큐에서 작업 하나 가져오기 (non-blocking)
            task = tasks_to_accomplish.get_nowait()
        except Empty:
            # 더 이상 작업이 없으면 종료
            break
        else:
            print(f"Task no {task}")
            time.sleep(0.5)  # 작업 수행 시뮬레이션
            result = f"Task no {task} is done by {current_process().name}"
            tasks_that_are_done.put(result)

if __name__ == "__main__":
    # 작업 큐와 결과 큐 생성
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    # 10개의 작업(Task no 0 ~ 9)을 큐에 넣기
    for i in range(10):
        tasks_to_accomplish.put(i)

    # 4개의 프로세스 생성
    processes = []
    for _ in range(4):
        p = Process(target=worker, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # 모든 프로세스 종료 대기
    for p in processes:
        p.join()

    # 모든 작업 완료 메시지 출력
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())