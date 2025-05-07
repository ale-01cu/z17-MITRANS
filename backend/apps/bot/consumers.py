from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from apps.classification.ml.model_loader import predict_comment_label
from datetime import datetime
import uuid

class ChatConsumer(AsyncWebsocketConsumer):
    # Diccionario de clase para seguimiento de bots por sala
    web_channels = {}
    bot_channels = {}
    is_bot_active = False  # Renombrar la variable de clase del estado del bot

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.user_type = self.scope['url_route']['kwargs']['user_type']

        # Unirse al grupo (esto puede ir antes de accept si lo prefieres)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Conexión establecida: {self.user_type} en {self.room_name}")

        # Registrar el canal del bot y enviar estado SI LA CONEXIÓN WEB FUE ACEPTADA
        if self.user_type == 'bot':
            self.__class__.bot_channels[self.room_group_name] = self.channel_name
            self.is_bot_active = True
            print(f"{self.user_type} registrado en sala: {self.room_name}")
            print(self.is_bot_active)
            await self.send_to_web(
                {
                    'bot': self.is_bot_active,
                    'type': 'bot_status',
                    'content': {'bot_status': self.is_bot_active},
                    'sender': 'system'
                }
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'bot': self.is_bot_active,
                    'type': 'bot_status',
                    'content': {'bot_status': 'disconnected'},
                    'status': 'disconnected',  # Indica que el bot está desconectado
                    'message': 'El bot se ha desconectado de la sala.',  # mensaje
                }
            )

        elif self.user_type == 'web':
            print(f"{self.user_type} registrado en sala: {self.room_name}")

            # Enviar el estado del bot al conectar el cliente web
            await self.send_to_web(
                {
                    'bot': self.is_bot_active,
                    'type':'bot_status',
                    'content':{'bot_status': self.is_bot_active},
                    'sender': 'system'
                }
            )
            if not self.is_bot_active:
                await self.send_to_web(
                    {
                        'bot': self.is_bot_active,
                        'type': 'bot_status',
                        'content': {'bot_status': self.is_bot_active},
                        'sender': 'system'}
                )


    async def disconnect(self, close_code):
        # Limpiar registro del bot si se desconecta
        if self.user_type == 'bot' and self.__class__.bot_channels.get(self.room_group_name) == self.channel_name:
            self.is_bot_active = False  # Usar el nuevo nombre
            print(f"Bot desconectado de: {self.room_name}")
            print(self.is_bot_active)
            await self.send_to_web(self.is_bot_active)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'bot': self.is_bot_active,
                    'type': 'bot.status',
                    'content': {'bot_status': 'disconnected'},
                    # 'status': 'disconnected',  # Indica que el bot está desconectado
                    'message': 'El bot se ha desconectado de la sala.',  # mensaje
                }
            )


        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            sender = data.get('sender')
            content = data.get('content')
            message_id = data.get('message_id')
            timestamp_str = data.get('timestamp')
            print("data: ", data)

            # Enviar ACK inmediatamente si el mensaje tiene message_id
            if message_id:
                ack_message = {
                    'type': 'ack',
                    'message_id': message_id,
                    'status': 'received',
                    'timestamp': datetime.now().isoformat()
                }
                await self.send(text_data=json.dumps(ack_message))

            # Resto de tu lógica existente...
            if message_type == 'control_bot' and sender == 'web':
                await self.handle_bot_control(data.get('action'))
                return

            if sender == 'bot':
                await self.process_bot_message(content)
            elif sender == 'web':
                await self.process_web_message(content)

        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error procesando mensaje'
            }))

    async def bot_status(self, event):
        status = event['status']
        message = event['message']

        # Envia el estado del bot al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'bot.status',
            'status': status,
            'message': message
        }))

    async def handle_bot_control(self, action):
        """Controla el bot desde el frontend, pausando o reanudando su actividad."""
        bot_channel = self.__class__.bot_channels.get(self.room_group_name)

        if bot_channel:
            # Importar el módulo del bot
            import machine_learning.bot.bot

            if action == 'disconnect':
                # Pausar el bot
                machine_learning.bot.bot.is_paused = True  # Establecer is_paused en True para pausar
                self.__class__.is_bot_active = False  # Usar el nuevo nombre
                print('Bot pausado')
                print(self.is_bot_active)
                await self.notify_group('system', 'Bot pausado')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bot.status',
                        'status': 'disconnected',  # Indica que el bot se ha desconectado
                        'message': 'El bot ha sido pausado por un usuario.',
                    }
                )

            elif action == 'connect':
                # Reanudar el bot
                machine_learning.bot.bot.is_paused = False  # Establecer is_paused en False para reanudar
                self.__class__.is_bot_active = True  # Usar el nuevo nombre
                print('Bot reanudado')  # mejorar el mensaje
                print(self.is_bot_active)
                await self.notify_group('system', 'Bot reanudado')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bot.status',
                        'status': 'connected',  # Indica que el bot se ha conectado
                        'message': 'El bot ha sido reanudado por un usuario.',
                    }
                )
            else:
                print(f"Acción desconocida: {action}")  # siempre es bueno tener un else
                await self.notify_group('system', f'Acción desconocida: {action}')
        else:
            print("No se encontró el canal del bot para esta sala.")  # debug
            await self.notify_group('system', 'No se encontró el canal del bot para esta sala.')
            print(self.is_bot_active)


    async def process_bot_message(self, content_data):
        from apps.comment.models import Comment
        from apps.classification.models import Classification
        from apps.source.models import Source

        message = content_data.get('message')
        chat_id = content_data.get('chat_id')
        label = ''

        # Paso 1: Predecir la etiqueta (siempre se ejecuta)
        if message:
            label = predict_comment_label(message)  # <-- Predicción fuera del try-except

        # Paso 2: Intentar guardar en BD (manejando errores)
        try:
            if message and chat_id:
                classification = await sync_to_async(Classification.objects.get)(name=label)
                source = await sync_to_async(Source.objects.get)(name='Messenger')  # Asegúrate de que existe

                await sync_to_async(Comment.objects.create)(
                    text=message,
                    classification=classification,
                    source=source
                )
        except Exception as e:
            print(f"Error en BD: {str(e)}")  # Log del error, pero no se detiene el flujo

        # Paso 3: Enviar a la web (SIEMPRE se ejecuta)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message',
                'content': {
                    'message': message,
                    'label': label,
                    'chat_id': chat_id
                },
                'sender': 'bot',
            }
        )

    async def process_web_message(self, content):
        """Procesa mensajes entrantes del frontend"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message',
                'content': content,
                'sender': 'web'
            }
        )

    # esto para en un futuro ver el estado de el bot siempre que haga falta
    # async def send_status(self, content):
    #     if self.is_bot_active:
    #         await self.send(self.is_bot_active)
    #         print('Enviando estado a la web')


    async def send_to_web(self, event):
        """Envía mensajes a los clientes web"""
        if self.user_type == 'web':
            await self.send(text_data=json.dumps({
                'bot': bool(self.is_bot_active),  # Usar el nuevo nombre
                'type': event['type'],
                'content': event['content'],
                'sender': event['sender'],
            }))

    async def send_to_bot(self, event):
        """Envía mensajes al bot"""
        if self.user_type == 'bot':
            await self.send(text_data=json.dumps({

                'type': 'message',
                'content': event['content'],
                'sender': event['sender'],
                'message_id': str(uuid.uuid4())  # Añadir ID único para el ACK
            }))

    async def notify_group(self, msg_type, message):
        """Notifica al grupo"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_to_web',
                'content': {'message': message},
                'sender': 'system'
            }
        )