import queue
import sys
import collections
import time
import threading

import numpy as np

import config
import read_serial
import process

raw_data = collections.deque(maxlen=config.WINDOW_SIZE + config.AVG_W)

server_thread = None
server_on = True


def start_server():
    global raw_data
    q = queue.Queue()
    read_serial.open_connection(q)  # Non-blocking!

    def server_worker():
        cnt = 0
        while server_on:
            raw_data.append(q.get())  # q 阻塞…… join的时候可能会卡死
            cnt += 1
            if cnt == config.STEP_SIZE:
                cnt = 0
                process.start_processing()
        read_serial.close_connection()
    server_thread = threading.Thread(target=server_worker)
    server_thread.start()


def stop_server():
    server_on = False
    global server_thread
    if server_thread:
        server_thread.join()
    else:
        print("[stop_server]: no server thread to join!")
    print("[stop_server] : server stopped")


if __name__ == "__main__":
    start_server()
    while True:
        print(np.asarray(list(raw_data)).shape)
        time.sleep(1)
