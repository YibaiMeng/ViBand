import asyncio
import time
import json
import signal
import multiprocessing

import websockets

import presentation


curr_page = 0


def worker(conn, q):
    async def service(conn, q):
        async with websockets.connect('wss://viband.mengyibai.cn/viband', ping_timeout=None) as websocket:
            global curr_page
            while True:
                if websocket.closed:
                    print("Shit!, closed!")
                if not q.empty():
                    command = q.get(timeout=3)#conn.recv()
                else: 
                    command = None
                if command == "next":
                    curr_page += 1
                    send_next_page = False
                    await websocket.send(json.dumps({"action": 'change', "value": {'indexh': curr_page, 'indexv': 0, 'paused': False, 'overview': False}}))
                    print('cmd sent!')
                elif command == "previous":
                    curr_page -= 1
                    send_prev_page = False
                    await websocket.send(json.dumps({"action": 'change', "value": {'indexh': curr_page, 'indexv': 0, 'paused': False, 'overview': False}}))
                    print("previous sent!")
                elif command == "die":
                    break
                else:
                    websocket.ping()
    asyncio.get_event_loop().run_until_complete(service(conn,q))