#!/usr/bin/env python

import ssl
import pathlib
import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {'value': 0}

USERS = set()

def state_event():
    return json.dumps({'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})

async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_users():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        #STATE['value'] = {'indexh': 1, 'indexv': 0, 'paused': False, 'overview': False}
        async for message in websocket:
            data = json.loads(message)
            if data['action'] == 'change': # My local version is like this. But the distributed version does not contain any code.
                STATE['value'] = data['value']
                print("state is now", STATE['value'])
                await notify_state()
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregister(websocket)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    pathlib.Path(__file__).with_name('key.pem'))

asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, 'localhost', 8765, ssl=ssl_context))
asyncio.get_event_loop().run_forever()
