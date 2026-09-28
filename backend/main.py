from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="okDriver CCTV Analytics Platform")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections store
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# Sample Cameras Data
CAMERAS_DATA = [
    {"id": "C001", "name": "SG Highway Node", "latitude": 23.0225, "longitude": 72.5714},
    {"id": "C002", "name": "Iscon Junction", "latitude": 23.0275, "longitude": 72.5814},
    {"id": "C003", "name": "Prahlad Nagar", "latitude": 23.0125, "longitude": 72.5014},
]

@app.get("/api/v1/cameras")
def get_cameras():
    return CAMERAS_DATA

@app.get("/api/v1/trace/{vehicle_no}")
def trace_route(vehicle_no: str):
    return [
        {"latitude": 23.0225, "longitude": 72.5714, "timestamp": "10:00 AM"},
        {"latitude": 23.0275, "longitude": 72.5814, "timestamp": "10:05 AM"},
        {"latitude": 23.0125, "longitude": 72.5014, "timestamp": "10:10 AM"},
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/v1/trigger_alert")
async def trigger_alert(alert: dict):
    await manager.broadcast(alert)
    return {"status": "success", "broadcasted_to": len(manager.active_connections)}