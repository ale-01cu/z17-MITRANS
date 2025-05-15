from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from apps.classification.ml.model_loader import predict_comment_label
from datetime import datetime
import uuid


#esto es una prueba 
class ChatConsumer(AsyncWebsocketConsumer):
    # Diccionario para seguimiento del estado del bot por sala
    web_channels = {}
    bot_channels = {}
    room_bot_status = {}  # ✅ Estado del bot por sala

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.user_type = self.scope['url_route']['kwargs']['user_type']

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Conexión establecida: {self.user_type} en {self.room_name}")

        # Registrar el bot y actualizar estado
        if self.user_type == 'bot':
            self.__class__.bot_channels[self.room_group_name] = self.channel_name
            # self.__class__.room_bot_status[self.room_group_name] = True  # ✅ Estado por sala

            print(f"{self.user_type} registrado en sala: {self.room_name}")
            bot_status = self.room_group_name in self.__class__.bot_channels
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bot_status',
                    'content': {'bot_status': True},
                    'bot_status': bot_status,
                    'status': 'connected' if bot_status else 'disconnected',
                    'message': 'El bot se ha conectado a la sala.',
                    'sender': 'system'
                }
            )


        elif self.user_type == 'web':
            # Verificar si el bot está en la sala usando bot_channels (fuente confiable)
            bot_status = self.room_group_name in self.__class__.bot_channels
            await self.send(text_data=json.dumps({
                'type': 'bot_status',
                'bot_status': bot_status,
                'status': 'connected' if bot_status else 'disconnected',
                'message': 'Estado inicial del bot.',
                'sender': 'system'
            }
            ))

    async def disconnect(self, close_code):
        # Limpiar registro del bot si se desconecta
        if self.user_type == 'bot' and self.__class__.bot_channels.get(self.room_group_name) == self.channel_name:
            del self.__class__.bot_channels[self.room_group_name]  # ✅ Eliminar de bot_channels
            self.__class__.room_bot_status[self.room_group_name] = False
            print(f"Bot desconectado de: {self.room_name}")

            # Notificar a todos los clientes web
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bot_status',
                    'content': {'bot_status': False},
                    'status':'disconnected',
                    'message': 'El bot se ha desconectado de la sala.',
                    'sender': 'system'
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

            print("data: ", data)
            print('data :','sender', sender,message_type)

            # Enviar ACK si hay ID de mensaje
            if message_id:
                ack_message = {
                    'type': 'ack',
                    'message_id': message_id,
                    'status': 'received',
                    'timestamp': datetime.now().isoformat()
                }
                await self.send(text_data=json.dumps(ack_message))

            # Manejo de acciones
            if message_type == 'control.bot' :
                await self.handle_bot_control(data.get('action'))
                return

            if sender == 'bot':
                await self.process_bot_message(content)
            # elif sender == 'web':
            #     await self.process_web_message(content)

        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error procesando mensaje'
            }))

    async def bot_status(self, event):
        status = event['status']
        message = event['message']
        # Enviar estado del bot al cliente web
        await self.send(text_data=json.dumps({
            'type': 'bot_status',
            'status': status,
            'message': message
        }))

    async def handle_bot_control(self, action):
        """Controla el bot desde el frontend, pausando o reanudando su actividad."""
        bot_channel = self.__class__.bot_channels.get(self.room_group_name)
        print('aqui llegue')
        if bot_channel:
            import machine_learning.bot.bot
            if action == 'disconnect':
                machine_learning.bot.bot.is_paused = True
                self.__class__.room_bot_status[self.room_group_name] = False  # ✅ Estado por sala
                print('Bot pausado')
                bot_status = self.room_group_name in self.__class__.bot_channels
                print(bot_status)
                await self.channel_layer.group_send(
                    self.send_to_bot,
                    {
                        'type': 'bot_status',  # ✅ Corregir de 'bot_status'
                        'status':  'connected' if bot_status else 'disconnected',
                        'message': 'El bot ha sido pausado por un usuario.',
                        'sender': 'system'
                    }
                )
            elif action == 'connect':
                machine_learning.bot.bot.is_paused = False
                self.__class__.room_bot_status[self.room_group_name] = True  # ✅ Estado por sala
                print('Bot reanudado')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bot_status',  # ✅ Corregir de 'bot.status' a 'bot_status'
                        'status': 'connected',
                        'message': 'El bot ha sido reanudado por un usuario.',
                        'sender': 'web'
                    }
                )
            else:
                print(f"Acción desconocida: {action}")
                await self.notify_group('system', f'Acción desconocida: {action}')
        else:
            print("No se encontró el canal del bot para esta sala.")
            await self.notify_group('system', 'No se encontró el canal del bot para esta sala.')

    async def process_bot_message(self, content_data):
        from apps.comment.models import Comment
        from apps.classification.models import Classification
        from apps.source.models import Source
        message = content_data.get('message')
        chat_id = content_data.get('chat_id')
        label = ''

        if message:
            label = predict_comment_label(message)

        try:
            if message and chat_id:
                classification = await sync_to_async(Classification.objects.get)(name=label)
                source = await sync_to_async(Source.objects.get)(name='Messenger')
                await sync_to_async(Comment.objects.create)(
                    text=message,
                    classification=classification,
                    source=source
                )
        except Exception as e:
            print(f"Error en BD: {str(e)}")

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

    async def send_to_web(self, event):
        """Envía mensajes a los clientes web"""
        if self.user_type == 'web':
            await self.send(text_data=json.dumps({
                'bot': self.__class__.room_bot_status.get(self.room_group_name, False),
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
                'message_id': str(uuid.uuid4())
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