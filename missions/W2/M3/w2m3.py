from multiprocessing import Queue

def push(q, colors):
    print("pushing items to queue:")
    for i, color in enumerate(colors, start=1):
        q.put(color)
        print(f"item no: {i} {color}")
    
    # sentinel
    q.put(None)
    q.put(None)

def pop(q):
    print("popping items from queue:")
    i = 0
    while True:
        item = q.get()
        if item is None:
            break
        print(f"item no: {i} {item}")
        i += 1     

if __name__ == "__main__":

    colors = ["red", "green", "blue", "black"]

    # queue 생성
    q = Queue()
    
    push(q, colors)
    pop(q)
