import asyncio
import json

from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI()

class JsonRPCRequest(BaseModel):
    method: str
    id: int
    jsonrpc: str
    params: Optional[dict] = {}
    
class Connection:
    def __init__(self, websocket: WebSocket, dongle_id: str, duplicates: int):
        self.websocket = websocket
        self.duplicates = duplicates
        self.dongle_id = dongle_id
        self.priority = 0
        self.recv_queue = asyncio.PriorityQueue()   

    def handle(self, response):
        priority = response['id']
        self.recv_queue.put_nowait((priority,response))

class ConnectionCollection:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, dongle_id: str, websocket: WebSocket):
        await websocket.accept()
        duplicate = 0
        if dongle_id in self.active_connections:
            duplicate = self.active_connections[dongle_id].duplicates + 1
        
        self.active_connections[dongle_id] = Connection(websocket, dongle_id, duplicate)

    def disconnect(self, dongle_id: str):
        if dongle_id in self.active_connections:
            if self.active_connections[dongle_id].duplicates > 0:
                self.active_connections[dongle_id].duplicates = self.active_connections[dongle_id].duplicates - 1
            else:
                self.active_connections.pop(dongle_id)

    def get_connection(self, dongle_id: str)-> Connection:
        if dongle_id in self.active_connections:
            return self.active_connections[dongle_id]
        else:
            return None

    async def send(self, uid: int, request: JsonRPCRequest, connection: Connection):   
        data = request.dict()
        data['id'] = uid        
        await connection.websocket.send_text(json.dumps(data))

    async def request(self, dongle_id: str, request: JsonRPCRequest):
        connection = self.get_connection(dongle_id)
        if connection:         
            uid = connection.priority
            await self.send(uid, request, connection)
            connection.priority += 1
            return await manager.receive(uid, connection)
        else:
            return {
                'error': {
                    'message': 'No connection found'
                }            
            } 

    async def receive(self, uid: int, connection: Connection):
        while connection.dongle_id in self.active_connections:
            try:               
                response = await connection.recv_queue.get()
                if response[1]['id'] != uid:
                    connection.recv_queue.put_nowait(response)    
                    await asyncio.sleep(0.2)               
                else:
                    return response[1]
            except:
                pass

manager = ConnectionCollection()

@app.post("/{dongle_id}")
async def rest_endpoint(dongle_id: str, request: JsonRPCRequest):
    return await manager.request(dongle_id, request)


@app.websocket("/{dongle_id}")
async def websocket_endpoint(websocket: WebSocket, dongle_id: str):
    await manager.connect(dongle_id, websocket)
    connection = manager.get_connection(dongle_id)
    try:
        while True:
            response = await websocket.receive_json()
            connection.handle(response)
    except WebSocketDisconnect:
        manager.disconnect(dongle_id)

