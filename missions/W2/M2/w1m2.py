from multiprocessing import Process

# 대륙 이름 출력 함수
def print_continent(continent="Asia"):
    print(f"The name of continent is : {continent}")

if __name__ == "__main__":
    processes = []

    # 기본값(Asia)으로 실행
    p_default = Process(target=print_continent)
    processes.append(p_default)

    # 다른 대륙 이름으로 실행
    for name in ["America", "Europe", "Africa"]:
        p = Process(target=print_continent, args = [name])
        processes.append(p)

    # 모든 프로세스 시작
    for p in processes:
        p.start()

    # 모든 프로세스가 끝날 때까지 대기
    for p in processes:
        p.join()