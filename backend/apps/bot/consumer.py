from channels.generic.websocket import WebsocketConsumer
import json

import json
from channels.generic.websocket import WebsocketConsumer


import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("Conexión WebSocket establecida")

        # Añadir la conexión al grupo "chat"
        self.room_group_name = "chat"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Aceptar la conexión
        self.accept()

        # Enviar un mensaje de bienvenida al cliente
        self.send(text_data=json.dumps({
            'message': '¡Bienvenido!',
            'status': 'conectado'
        }))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": "Bienvenido"
            }
        )

    def disconnect(self, close_code):
        print("Conexión WebSocket cerrada")

        # Eliminar la conexión del grupo "chat"
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if 'text' in data:
                mensaje_recibido = data['data']

                # Preparar respuesta
                respuesta = {
                    'message': mensaje_recibido,
                    'status': 'recibido'
                }

                # Broadcast: Enviar el mensaje a todos los clientes en el grupo
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": 'Bienvenido'
                    }
                )

            else:
                print(f"Datos recibidos sin formato correcto: {data}")
                self.send(text_data=json.dumps({
                    'error': 'Formato incorrecto',
                    'message': 'Envía un JSON con formato {"text": "tu mensaje"}'
                }))

        except json.JSONDecodeError:
            print(f"Error: Mensaje no es JSON válido. Datos recibidos: {text_data}")
            self.send(text_data=json.dumps({
                'error': 'Formato inválido',
                'message': 'Envía un JSON con formato {"text": "tu mensaje"}'
            }))

    # Método para manejar mensajes enviados al grupo
    def chat_message(self, event):
        message = event["message"]

        print('aaaaaaaaaaaaaaaaaaaaa')
        print(message)
        # Enviar el mensaje a todos los clientes en el grupo
        self.send(text_data=json.dumps({
            "message": message,
            "status": "broadcast"
        }))