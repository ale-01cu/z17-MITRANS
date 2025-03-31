import websockets
import asyncio
import json
from typing import Optional, Callable
import logging

class WebSocketClient:
    def __init__(self, uri: str, on_message: Optional[Callable] = None):
        self.uri = uri
        self.connection: Optional[websockets.WebSocketClientProtocol] = None
        self.on_message = on_message
        self.is_connected = False
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        """Establishes connection with the WebSocket server"""
        try:
            self.connection = await websockets.connect(self.uri)
            self.is_connected = True
            self.logger.info(f"Connected to WebSocket server at {self.uri}")
            
            # Start listening for messages
            asyncio.create_task(self._listen())
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {e}")
            return False

    async def disconnect(self):
        """Closes the WebSocket connection"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            self.logger.info("Disconnected from WebSocket server")

    async def send_message(self, message: dict):
        """Sends a message to the WebSocket server"""
        if not self.is_connected:
            self.logger.warning("Not connected to server. Attempting to reconnect...")
            await self.connect()
            
        if self.connection:
            try:
                await self.connection.send(json.dumps(message))
                self.logger.debug(f"Sent message: {message}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")
                return False
        return False

    async def _listen(self):
        """Listens for incoming messages from the server"""
        while self.is_connected:
            try:
                message = await self.connection.recv()
                data = json.loads(message)
                
                if self.on_message:
                    await self.on_message(data)
                
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("WebSocket connection closed")
                self.is_connected = False
                break
            except Exception as e:
                self.logger.error(f"Error while listening for messages: {e}")
                break