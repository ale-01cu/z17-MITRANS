from channels.generic.websocket import WebsocketConsumer
import json

import json
from channels.generic.websocket import WebsocketConsumer


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Este consumer debe de atender a un bot y devolver lo que envie.
    El bot encia datos y este consumer debe de devolver esos datos tal cual los envia el bot.

    Entrada: {
        type: str,
        data: {
            chat_id: str,
            message: str,
            "bot_name": str,
            "timestamp": str
        }
    }

    Salida: {
        type: str,
        data: {
            chat_id: str,
            message: str
        }
    }

    """

    def __init__(self):
        super().__init__()

    async def connect(self):
        print("Conexión WebSocket establecida")

        # Añadir la conexión al grupo "chat"
        self.room_group_name = "general_communication"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Aceptar la conexión
        await self.accept()

    async def disconnect(self, close_code):
        print("Conexión WebSocket cerrada")

        # Eliminar la conexión del grupo "chat"
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # message_type = text_data_json.get('type')
        message_content = text_data_json.get('content')
        sender = text_data_json.get('sender')  # 'web' o 'bot'

        print("data: ", text_data_json)

        # Reenviar el mensaje al grupo correspondiente
        if sender == 'bot':
            # Mensaje de bot a web
            print("manda a la web")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_to_web',
                    'content': message_content,
                    'sender': 'bot'
                }
            )
        elif sender == 'web':
            # Mensaje de web a bot
            print("manda a; bot")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_to_bot',
                    'content': message_content,
                    'sender': 'web'
                }
            )

    # Método para manejar mensajes enviados al grupo
    # def bot_message(self, event):
    #     data = event["data"]
    #
    #     print('aaaaaaaaaaaaaaaaaaaaa')
    #     # Enviar el mensaje a todos los clientes en el grupo
    #     self.send(text_data=json.dumps({
    #         'type': 'broadcast',
    #         'data': data
    #     }))

    async def send_to_web(self, event):
        print("manda a la web group")

        content = event['content']
        sender = event['sender']

        # Enviar solo si el cliente es web
        if sender == 'bot':
            await self.send(text_data=json.dumps({
                'type': 'message',
                'content': content,
                'sender': 'bot'
            }))

    # Handler para mensajes destinados al bot
    async def send_to_bot(self, event):
        print("manda a la bot")

        content = event['content']
        sender = event['sender']

        # Enviar solo si el cliente es bot
        if sender == 'web':
            await self.send(text_data=json.dumps({
                'type': 'message',
                'content': content,
                'sender': 'web'
            }))