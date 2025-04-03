import websockets
import asyncio
import json
from typing import Optional, Callable
import logging

import asyncio
import websockets
import json
import logging
from typing import Optional, Callable, Dict, Any
import uuid
from datetime import datetime

class WebSocketClient:
    def __init__(self, uri: str, on_message: Optional[Callable] = None):
        self.uri = uri
        self.connection: Optional[websockets.WebSocketClientProtocol] = None
        self.on_message = on_message
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._pending_messages = asyncio.Queue()
        self._message_callbacks = {}  # Para manejar ACKs
        self._keepalive_task = None
        self._listen_task = None
        self._send_task = None

    async def connect(self) -> bool:
        """Establishes connection with the WebSocket server with retry logic"""
        if self.is_connected:
            return True
            
        try:
            self.connection = await websockets.connect(
                self.uri,
                ping_interval=20,    # Send ping every 20 seconds
                ping_timeout=60,      # Wait 60 seconds for pong response
                close_timeout=None,   # Don't timeout on close
                max_queue=2**20       # Increase message queue size
            )
            self.is_connected = True
            self._reconnect_attempts = 0
            self.logger.info(f"Connected to WebSocket server at {self.uri}")
            
            # Start background tasks
            self._keepalive_task = asyncio.create_task(self._keepalive())
            self._listen_task = asyncio.create_task(self._listen())
            self._send_task = asyncio.create_task(self._process_send_queue())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {e}")
            await self._handle_reconnect()
            return False

    async def disconnect(self):
        """Closes the WebSocket connection gracefully"""
        if self._keepalive_task:
            self._keepalive_task.cancel()
        if self._listen_task:
            self._listen_task.cancel()
        if self._send_task:
            self._send_task.cancel()
            
        if self.connection:
            try:
                await self.connection.close()
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")
            finally:
                self.connection = None
                self.is_connected = False
                self.logger.info("Disconnected from WebSocket server")

    async def send_message(self, message: Dict[str, Any], require_ack: bool = False, timeout: float = 5.0) -> bool:
        """
        Sends a message to the WebSocket server with optional ACK verification
        Args:
            message: The message to send
            require_ack: Whether to wait for server acknowledgment
            timeout: Timeout in seconds to wait for ACK
        Returns:
            bool: True if message was sent (and acknowledged if required)
        """
        if not self.is_connected:
            self.logger.warning("Not connected to server. Adding to queue and attempting to reconnect...")
            print("Not connected to server. Adding to queue and attempting to reconnect...")
            await self._pending_messages.put((message, require_ack, timeout))
            await self.connect()
            return False

        message_id = str(uuid.uuid4())
        message_with_id = {**message, 'message_id': message_id, 'timestamp': datetime.now().isoformat()}

        try:
            if require_ack:
                ack_event = asyncio.Event()
                self._message_callbacks[message_id] = ack_event

            await self.connection.send(json.dumps(message_with_id))
            self.logger.debug(f"Sent message (ID: {message_id}): {message}")
            print(f"Sent message (ID: {message_id}): {message}")

            if require_ack:
                try:
                    await asyncio.wait_for(ack_event.wait(), timeout=timeout)
                    self.logger.debug(f"Message acknowledged (ID: {message_id})")
                    print(f"Message acknowledged (ID: {message_id})")
                    return True
                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout waiting for ACK (ID: {message_id})")
                    print(f"Timeout waiting for ACK (ID: {message_id})")
                    return False
            return True

        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Connection closed while sending. Adding to queue...")
            print("Connection closed while sending. Adding to queue...")
            await self._pending_messages.put((message, require_ack, timeout))
            self.is_connected = False
            await self._handle_reconnect()
            return False
        except Exception as e:
            self.logger.error(f"Failed to send message (ID: {message_id}): {e}")
            print(f"Failed to send message (ID: {message_id}): {e}")
            return False

    async def _listen(self):
        """Listens for incoming messages from the server"""
        while self.is_connected:
            try:
                message = await self.connection.recv()
                data = json.loads(message)
                self.logger.debug(f"Received message: {data}")
                
                # Handle ACKs first
                if data.get('type') == 'ack':
                    message_id = data.get('ack_message_id')
                    if message_id in self._message_callbacks:
                        self._message_callbacks[message_id].set()
                        del self._message_callbacks[message_id]
                    continue
                
                # Send ACK if requested
                if data.get('requires_ack'):
                    await self.connection.send(json.dumps({
                        'type': 'ack',
                        'ack_message_id': data.get('message_id')
                    }))
                
                # Process message
                if self.on_message:
                    try:
                        await self.on_message(data)
                    except Exception as e:
                        self.logger.error(f"Error in on_message callback: {e}")
                        
            except websockets.exceptions.ConnectionClosed as e:
                self.logger.warning(f"WebSocket connection closed: {e}")
                self.is_connected = False
                await self._handle_reconnect()
                break
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode message: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error while listening: {e}")
                self.is_connected = False
                await self._handle_reconnect()
                break

    async def _process_send_queue(self):
        """Processes messages in the send queue"""
        while self.is_connected:
            try:
                message, require_ack, timeout = await self._pending_messages.get()
                if not self.is_connected:
                    await self.connect()
                
                success = await self.send_message(message, require_ack, timeout)
                if not success:
                    await self._pending_messages.put((message, require_ack, timeout))
                    await asyncio.sleep(1)  # Prevent tight loop
                    
            except Exception as e:
                self.logger.error(f"Error processing send queue: {e}")
                await asyncio.sleep(1)

    async def _keepalive(self):
        """Maintains connection with keepalive pings"""
        while self.is_connected:
            try:
                await asyncio.sleep(15)  # Send ping every 15 seconds
                if self.is_connected and self.connection:
                    await self.connection.ping()
            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("Connection closed during keepalive")
                self.is_connected = False
                await self._handle_reconnect()
                break
            except Exception as e:
                self.logger.error(f"Keepalive error: {e}")
                self.is_connected = False
                await self._handle_reconnect()
                break

    async def _handle_reconnect(self):
        """Handles reconnection logic with exponential backoff"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            return
            
        self._reconnect_attempts += 1
        delay = min(2 ** self._reconnect_attempts, 30)  # Exponential backoff with max 30s
        
        self.logger.info(f"Attempting to reconnect in {delay} seconds (attempt {self._reconnect_attempts})")
        await asyncio.sleep(delay)
        await self.connect()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()