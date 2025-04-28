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
import time

class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.connection: Optional[websockets.WebSocketClientProtocol] = None
        self.on_message = self.handle_websocket_message
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

    async def _connect(self) -> bool:
        """Improved connection with better error handling"""
        print("test 1")
        async with self._lock:
            if self.is_connected:
                return True

            print("test 2")

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
                print("test 3")

                self.is_connected = True
                self._reconnect_attempts = 0
                print(f"Connected to WebSocket server at {self.uri}")
                self.logger.info(f"Connected to WebSocket server at {self.uri}")
                
                # Start background tasks
                self._keepalive_task = asyncio.create_task(self._keepalive())
                self._listen_task = asyncio.create_task(self._listen())
                self._send_task = asyncio.create_task(self._process_send_queue())

                print("test 4")

                return True
                
            except (asyncio.TimeoutError, OSError) as e:
                print(f"Connection timeout: {e}")
                self.logger.error(f"Connection timeout: {e}")
                return False
            except Exception as e:
                print(f"Unexpected connection error: {e}")
                self.logger.error(f"Unexpected connection error: {e}")
                return False

    async def test_connection(self):
        try:
            print("Conectando...")
            async with websockets.connect(self.uri) as ws:
                print("¡Conectado!")
                await ws.send("test")
                print(await ws.recv())
        except Exception as e:
            print(f"Error: {e}")


    async def _send_message(self, message: Dict[str, Any], require_ack: bool = True, timeout: float = None) -> bool:
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
                    await self._connect()
                
                success = await self._send_message(message, require_ack, timeout)
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
        await self._connect()

    async def __aenter__(self):
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


    async def connect_websocket(self):
        """Connects to the WebSocket server"""
        return await self._connect()


    async def disconnect_websocket(self):
        """Disconnects from the WebSocket server"""
        await self.disconnect()


    async def send_websocket_message(self, message_type: str, message: str, current_chat_id: str, name: str):
        """Improved message sending with error handling"""
        print("Mandando mensaje...")
        message_data = {
            "type": message_type,
            "sender": 'bot',
            "content": {
                "chat_id": current_chat_id,
                "message": message,
                "bot_name": name,
                "timestamp": time.time(),
                "sequence": int(time.time() * 1000)  # Add sequencing
            }
        }

        try:
            success = await self._send_message(message_data, require_ack=False)
            print("success ", success)
            if not success:
                print(f"Falló el envío del mensaje, reintentando...")
                await asyncio.sleep(1)
                return await self.send_websocket_message(message_type, message)

            print("Mensaje enviado correctamente con ACK")
            return True

        except Exception as e:
            print(f"Error crítico enviando mensaje: {e}")
            await self._disconnect()
            await self._connect()
            return False


    async def handle_websocket_message(self, message: dict):
        """Handles incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            data = message.get("data")

            if message_type == "command":
                # Handle different commands
                if data.get("action") == "stop":
                    # Handle stop command
                    pass
                elif data.get("action") == "start":
                    # Handle start command
                    pass
                # Add more command handlers as needed

        except Exception as e:
            print(f"Error handling WebSocket message: {e}")


    async def establish_connection(self):
        """Improved connection handling"""
        print("Conectando con el servidor...")

        # Connection loop with exponential backoff
        retry_delays = [1, 2, 5, 10, 30]
        for delay in retry_delays:
            if await self._connect():
                break
            print(f"Reintentando conexión en {delay} segundos...")
            await asyncio.sleep(self._max_reconnect_attempts)
        else:
            print("Failed to establish WebSocket connection after multiple attempts")
            return

        # Start monitoring task
        # asyncio.create_task(self._connection_monitor())


    async def _connection_monitor(self):
        """New connection health monitor"""
        while True:
            if not self.is_connected:
                print("Conexión perdida, intentando reconectar...")
                await self.establish_connection()

            await asyncio.sleep(5)
            # Send heartbeat
            try:
                await self._send_message({
                    "type": "heartbeat",
                    "content": "ping"
                }, require_ack=False)
            except:
                pass
