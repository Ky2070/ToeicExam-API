from typing import Dict, Set
from threading import Lock
import json
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class SSEManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SSEManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """Initialize the SSE manager"""
        self.connections: Dict[int, Set[asyncio.Queue]] = {}
        self.connection_lock = Lock()

    def register_connection(self, user_id: int, queue: asyncio.Queue):
        """Register a new SSE connection for a user"""
        with self.connection_lock:
            if user_id not in self.connections:
                self.connections[user_id] = set()
            self.connections[user_id].add(queue)

    def remove_connection(self, user_id: int, queue: asyncio.Queue):
        """Remove an SSE connection for a user"""
        with self.connection_lock:
            if user_id in self.connections:
                self.connections[user_id].discard(queue)
                if not self.connections[user_id]:
                    del self.connections[user_id]

    async def send_event(self, user_id: int, event_type: str, data: dict):
        """Send an event to all connections for a user"""
        with self.connection_lock:
            if user_id in self.connections:
                message = {"type": event_type, "data": data}
                for queue in self.connections[user_id]:
                    await queue.put(json.dumps(message))

    def notify_logout(self, user_id: int):
        """Send a force logout notification to all user's connections"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "force_logout",
                "message": "Your account was logged in from another device.",
            },
        )


# Global SSE manager instance
sse_manager = SSEManager()
