import logging 
from typing import List 
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections : List[WebSocket] = []
        
    async def connect(self,websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        logger.info(
            f"New WS connection. Total active connections: {len(self.active_connections)}"
        )
            
            
    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WS connection is closed, Total active connections is {len(self.active_connections)}"
            )
            
    async def broadcast(self, message: dict):
        # Sending JSON-message to all connection to web-socket clients 
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error of sending in WS: {e}")
                await self.disconnect(connection)
                
manager = ConnectionManager()
ws_router = APIRouter()


@ws_router.websocket("/ws/analytics")
async def websocket_analytics_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
