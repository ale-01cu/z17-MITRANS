from channels.generic.websocket import WebsocketConsumer
import json


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("Conexión WebSocket establecida")
        self.accept()

    def disconnect(self, close_code):
        print("Conexión WebSocket cerrada")

    def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if 'text' in data:
                mensaje_recibido = data['text']
                # print(f"Mensaje recibido: {mensaje_recibido}")

                # Preparar respuesta
                respuesta = {
                    'message': mensaje_recibido,
                    'status': 'recibido'
                }

                # Enviar eco al cliente
                # self.send(text_data=json.dumps(respuesta))
                # print(f"Mensaje enviado de vuelta: {mensaje_recibido}")

            else:
                # print("Mensaje recibido sin formato correcto")
                print(f"Datos recibidos: {data}")

        except json.JSONDecodeError:
            # print("Error: Mensaje no es JSON válido")
            print(f"Datos  recibidos: {text_data}")
            self.send(text_data=json.dumps({
                'error': 'Formato inválido',
                'message': 'Envía un JSON con formato {"text": "tu mensaje"}'
            }))