import time
from multiprocessing import Pool

# 각 작업 시뮬레이션 함수
def work_log(each_work):
    name, execute_time = each_work
    print(f"Process {name} waiting {execute_time} seconds")
    time.sleep(execute_time)
    print(f"Process {name} Finished.")

if __name__ == "__main__":
    
    # 작업 정의
    work = [
        ("A", 5),
        ("B", 2),
        ("C", 1),
        ("D", 3),
    ]
    
    #워커 풀 설정
    with Pool(processes = 2) as pool:
        pool.map(work_log, work)