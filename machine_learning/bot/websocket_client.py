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
        self._lock = asyncio.Lock()  # Add thread safety
        self._connection_timeout = 10  # New connection timeout
        self._ack_timeout = 8  # Reduced ACK timeout

    async def connect(self) -> bool:
        """Improved connection with better error handling"""
        async with self._lock:
            if self.is_connected:
                return True
                
            try:
                self.connection = await asyncio.wait_for(
                    websockets.connect(
                        self.uri,
                        ping_interval=15,
                        ping_timeout=25,
                        close_timeout=None,
                        max_size=2**24  # Increased max message size (16MB)
                    ),
                    timeout=self._connection_timeout
                )
                self.is_connected = True
                self._reconnect_attempts = 0
                self.logger.info(f"Connected to WebSocket server at {self.uri}")
                
                # Start background tasks
                self._keepalive_task = asyncio.create_task(self._keepalive())
                self._listen_task = asyncio.create_task(self._listen())
                self._send_task = asyncio.create_task(self._process_send_queue())
                
                return True
                
            except (asyncio.TimeoutError, OSError) as e:
                self.logger.error(f"Connection timeout: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected connection error: {e}")
                return False

    async def send_message(self, message: Dict[str, Any], require_ack: bool = True, timeout: float = None) -> bool:
        async with self._lock:
            timeout = timeout or self._ack_timeout
            message_id = str(uuid.uuid4())
            message_with_id = {
                **message,
                'message_id': message_id,
                'timestamp': datetime.now().isoformat(),
                'retries': 0
            }
            print("ulala")
    
            max_retries = 3
            for attempt in range(max_retries):
                ack_event = asyncio.Event()
                self._message_callbacks[message_id] = ack_event
                
                try:
                    await self.connection.send(json.dumps(message_with_id))
                    self.logger.debug(f"Sent message (ID: {message_id}): {message}")
                    
                    if not require_ack:
                        return True
                    
                    try:
                        await asyncio.wait_for(ack_event.wait(), timeout=timeout)
                        self.logger.debug(f"Message acknowledged (ID: {message_id})")
                        return True
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Timeout waiting for ACK (ID: {message_id})")
                        # Don't return immediately, check connection status first
                        if not self.is_connected:
                            break  # Exit retry loop to attempt reconnect
                        continue  # Retry immediately if still connected

                except (websockets.exceptions.ConnectionClosed, OSError) as e:
                    self.logger.warning(f"Connection error (attempt {attempt+1}/{max_retries}): {e}")
                    await self._handle_reconnect()
                    await asyncio.sleep(1)
                finally:
                    # Always clean up the callback reference
                    if message_id in self._message_callbacks:
                        del self._message_callbacks[message_id]
    
                # Store message in persistent queue before retrying
                await self._pending_messages.put((message_with_id, require_ack, timeout))

                
            self.logger.error(f"Failed to send message after {max_retries} attempts")
            return False

    async def _listen(self):
        """Improved listener with message validation"""
        while self.is_connected:
            try:
                message = await asyncio.wait_for(self.connection.recv(), timeout=30)
                if not message:
                    continue
                    
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
            except asyncio.TimeoutError:
                self.logger.warning("No message received in 30 seconds, sending ping...")
                await self.connection.ping()
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