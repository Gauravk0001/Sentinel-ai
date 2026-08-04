"""
SentinelAI - WebSocket Manager
Real-time communication for live updates
"""

import asyncio
import json
from typing import Set, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import random


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat()
        }

        # Send welcome message
        await self.send_personal_message(client_id, {
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to SentinelAI real-time monitoring",
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]

    async def send_personal_message(self, client_id: str, message: dict):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception:
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(client_id)

        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast_alert(self, alert_data: dict):
        """Broadcast security alert to all clients"""
        await self.broadcast({
            "type": "new_alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        })

    async def broadcast_ai_alert(self, alert_data: dict):
        """Broadcast an AI-generated security alert to all clients"""
        await self.broadcast({
            "type": "ai_alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        })

    async def broadcast_risk_update(self, employee_id: str, risk_score: float):
        """Broadcast risk score update"""
        await self.broadcast({
            "type": "risk_update",
            "data": {
                "employee_id": employee_id,
                "risk_score": risk_score,
                "timestamp": datetime.now().isoformat()
            }
        })

    async def broadcast_dashboard_update(self, stats: dict):
        """Broadcast dashboard statistics update"""
        await self.broadcast({
            "type": "dashboard_update",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })

    def get_connected_count(self) -> int:
        """Get number of connected clients"""
        return len(self.active_connections)

    def get_connections_info(self) -> list:
        """Get info about all connections"""
        return [
            {"client_id": cid, **meta}
            for cid, meta in self.connection_metadata.items()
        ]


# Global connection manager instance
manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket, client_id: str = None):
    """Handle WebSocket connection lifecycle"""
    if client_id is None:
        client_id = f"client_{random.randint(10000, 99999)}"

    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            message_type = message.get("type", "")

            if message_type == "ping":
                await manager.send_personal_message(client_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

            elif message_type == "subscribe":
                channel = message.get("channel", "")
                await manager.send_personal_message(client_id, {
                    "type": "subscribed",
                    "channel": channel,
                    "message": f"Subscribed to {channel}"
                })

            elif message_type == "unsubscribe":
                channel = message.get("channel", "")
                await manager.send_personal_message(client_id, {
                    "type": "unsubscribed",
                    "channel": channel
                })

            elif message_type == "get_stats":
                await manager.send_personal_message(client_id, {
                    "type": "stats",
                    "data": {
                        "connected_clients": manager.get_connected_count(),
                        "active_connections": manager.get_connections_info()
                    }
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        manager.disconnect(client_id)
