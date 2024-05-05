import json
from collections import deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

active_connections = deque()
active_client_idx = 0


@app.websocket('/chat')
async def websocket_endpoint(websocket: WebSocket):
    global active_client_idx
    await websocket.accept()
    active_connections.append(websocket)
    if len(active_connections) == 2:
        active_client = active_connections[active_client_idx]
        await active_client.send_json({'active': True})
    try:
        while True:
            data = await websocket.receive_json()
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_json(data)
            active_client_idx += 1
            if active_client_idx == len(active_connections):
                active_client_idx = 0

    except WebSocketDisconnect:
        active_connections.remove(websocket)
