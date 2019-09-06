import asyncio
import time
import json
import multiprocessing
import signal

import websockets

import presentation_worker

q = None
p = None

t_next = time.time()
def next_page():
    global q, t_next
    if q:
        if time.time() - t_next < 5:
            return
        else:
            q.put("next")
            t_next = time.time()
    else:
        print("No connection!")
    send_next_page = True

t_prev = time.time()
def prev_page():
    global q, t_prev
    if q:
        if time.time() - t_prev < 5:
            return
        else:
            q.put("previous")
            t_prev = time.time()

    else:
        print("No connection!")


def start_presentation_server():
    global q, p
    #, child_conn = multiprocessing.Pipe()
    q = multiprocessing.Queue()
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    p = multiprocessing.Process(
        target=presentation_worker.worker, args=(None,q))
    signal.signal(signal.SIGINT, original_sigint_handler)
    p.start()


def stop_presentation_server():
    global q#, p
    q.put("die")
    #conn.close()
    #p.terminate()


# start_presentation_server()
##print("Not blocking!")
# next_page()
# time.sleep(1)
# next_page()
# time.sleep(1)
# prev_page()
# time.sleep(1)
# stop_presentation_server()
