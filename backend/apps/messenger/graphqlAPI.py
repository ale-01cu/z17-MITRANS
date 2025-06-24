# from datetime import time
# import schedule
from django.conf import settings
import requests

BASE_URL = settings.FACEBOOK_BASE_URL


class FacebookAPIGraphql:

    def __init__(self,
                 facebook_page_name: str = None,
                 facebook_access_token: str = None,
                 facebook_page_id: str = None):

        self.facebook_page_name = facebook_page_name
        self.facebook_access_token = facebook_access_token
        self.facebook_page_id = facebook_page_id


    def get_conversations(self, platform: str = "messenger"):
        """
        Obtiene todas las conversaciones de la página
        """
        url = f"{BASE_URL}/{self.facebook_page_id}/conversations"

        params = {
            "platform": platform,
            "access_token": self.facebook_access_token
        }
        response = requests.get(url, params=params)
        return response.json()


    def get_conversation_with_user(self, user_id: str, platform: str = "messenger"):
        """
        Obtiene la conversación con un usuario específico
        """
        url = f"{BASE_URL}/{self.facebook_page_id}/conversations"
        params = {
            "platform": platform,
            "user_id": user_id,
            "access_token": self.facebook_access_token
        }
        response = requests.get(url, params=params)
        return response.json()


    def get_messages(self, conversation_id: str):
        """
        Obtiene los mensajes de una conversación específica
        """
        url = f"{BASE_URL}/{conversation_id}"
        params = {
            "fields": "messages",
            "access_token": self.facebook_access_token
        }
        response = requests.get(url, params=params)
        return response.json()


    def get_message_details(self, message_id: str):
        """
        Obtiene detalles de un mensaje específico
        """
        url = f"{BASE_URL}/{message_id}"
        params = {
            "fields": "id,created_time,from,to,message",
            "access_token": self.facebook_access_token
        }
        response = requests.get(url, params=params)
        return response.json()


    def debug_graphqlAPI(self):
        converstions = self.get_conversations()

        for conversation in converstions['data']:
            messages = self.get_messages(conversation_id=conversation['id'])
            messages = messages['messages']['data']

            for msg in messages:
                msg_detail = self.get_message_details(message_id=msg['id'])
                id = msg_detail['id']
                message = msg_detail['message']
                user_from = msg_detail['from']['name']
                users_to = msg_detail['to']['data']

                print(f'Antes del bucle del print.')

                for user_to in users_to:
                    user_to_name = user_to['name']
                    print(f'Messages from {user_from} to {user_to_name} -> {message}')


    def send_text_message(self, psid, message_text):
        """
        Sends a text message to a user via Facebook Messenger using the Graph API.

        Args:
            psid (str): The Page-Scoped User ID (PSID) of the recipient.
            message_text (str): The text message to send.

        Returns:
            dict: JSON response from the API or None if an error occurred.
        """
        url = f"{BASE_URL}/{self.facebook_page_id}/messages"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "recipient": {
                "id": psid
            },
            "messaging_type": "RESPONSE",
            "message": {
                "text": message_text
            }
        }

        params = {
            "access_token": self.facebook_access_token
        }

        try:
            response = requests.post(url, json=payload, headers=headers, params=params)
            data = response.json()

            if "error" in data:
                print(f"Error sending message: {data['error']['message']}")
                return None

            print("Message sent successfully!")
            print(f"Recipient ID: {data.get('recipient_id')}")
            print(f"Message ID: {data.get('message_id')}")

            return data

        except Exception as e:
            print(f"An error occurred while sending the message: {str(e)}")
            return None

# def task_consult():
#     """
#     Esta función define la secuencia de acciones que se ejecutarán periódicamente.
#     """
#     print(f"--- Iniciando tarea periódica en: {time.ctime()} ---")
#
#     # Ejemplo: Obtener conversación para un usuario específico
#     user_id_ejemplo = "ID_DE_USUARIO_ESPECIFICO" # Reemplaza con un ID de usuario real o una lógica para obtenerlo
#     conversation_data = get_conversation_with_user(user_id_ejemplo)
#
#     if conversation_data and 'data' in conversation_data and conversation_data['data']:
#         # Suponiendo que la API devuelve una lista de conversaciones y tomamos la primera
#         conversation_id = conversation_data['data'][0]['id']
#         print(f"Conversación obtenida: {conversation_id}")
#
#         # Ahora, obtén los mensajes de esa conversación
#         messages_data = get_messages(conversation_id)
#
#         if messages_data and 'messages' in messages_data and 'data' in messages_data['messages']:
#             print(f"Mensajes obtenidos para {conversation_id}: {len(messages_data['messages']['data'])} mensajes.")
#             for message in messages_data['messages']['data']:
#                 message_id = message['id']
#                 # Opcionalmente, obtén detalles de cada mensaje
#                 # details = get_message_details(message_id)
#                 # if details:
#                 #     print(f"  Detalles del mensaje {message_id}: {details.get('message', 'N/A')}")
#                 print(f"  ID del Mensaje: {message_id}, Contenido: {message.get('message', 'N/A')}")
#         else:
#             print(f"No se encontraron mensajes o hubo un error para la conversación {conversation_id}")
#     else:
#         print(f"No se encontró conversación o hubo un error para el usuario {user_id_ejemplo}")
#     print("--- Tarea periódica finalizada ---")
#
# # --- 2. Programa la tarea ---
# # Puedes elegir diferentes unidades de tiempo:
# # schedule.every(10).minutes.do(mi_tarea_periodica)
# # schedule.every().hour.do(mi_tarea_periodica)
# # schedule.every().day.at("10:30").do(mi_tarea_periodica)
# # schedule.every(5).to(10).minutes.do(mi_tarea_periodica)
# # schedule.every().monday.do(mi_tarea_periodica)
# # schedule.every().wednesday.at("13:15").do(mi_tarea_periodica)
#
# # Para este ejemplo, la ejecutaremos cada 1 minuto.
# # ¡Ajusta esto según tus necesidades! Podría ser demasiado frecuente para algunas APIs.
#
# schedule.every(1).minutes.do(task_consult())
#
# # --- 3. Ejecuta el programador ---
# print("El programador de tareas ha iniciado. Presiona Ctrl+C para detener.")
# try:
#     while True:
#         schedule.run_pending() # Ejecuta todas las tareas que están pendientes
#         time.sleep(1)          # Espera 1 segundo antes de volver a comprobar
# except KeyboardInterrupt:
#     print("Programador detenido por el usuario.")


# Conversation Schema
# {
#   "data": [
#     {
#       "id": "t_1815074772554921",
#       "link": "/646437991888678/inbox/646929895172821/?section=messages",
#       "updated_time": "2025-05-26T13:55:33+0000"
#     },
#     // ... más conversaciones
#   ],
#   "paging": {
#     "cursors": {
#       "before": "QVFIUjVQSEZAsckxNdHBnZAWJLVk1Qb3lnTjd2WV8tamVkbWpZAYzVFakN6VDU3QTFXSWdBWV9PdnZA6UjJPMG9EQVFUM2MyY1hfV2QyZAkQ3amRESWFjU1hXM25waFI3Y0ZAldUVNU21Va1FSbkdrc2tNMDQ4U3NYTUlRV3J2VTNWdm13STNU",
#       "after": "QVFIUjhWZAGt4RW8ta2ExeERfTzdOMi1md1N2QnVIYUNCRDVWeThHbU1GelMzVk9iSmNoTWF3LTVueTdYeFp3Ti0yUkpfVTRBWjc4YVNKRTBWMUNrZAGZA0ZA0dIc1dMM1hZASEFGaUUtUl9OWk52bGo2UXhNM09QeXpKX1I4bVJtNzlGODhq"
#     }
#   }
# }




# Messages Schema
# [
#   {
#     "id": "m_K6BpO2h5AIaIZjsg91IKSFyUUY-epFURbR-dTNyx9YckWy5ECOoQdMmo3sSp9XqD0UWdg4FnIrlrnMoQf-fLDA",
#     "created_time": "2025-05-26T13:55:33+0000"
#   },
#   {
#     "id": "m_RQFfIr-81fLVxLFDvH_WAFyUUY-epFURbR-dTNyx9YfJnTlI0Rca-0vA7Keh0pFCq-hlb0cmaAxq445DUW04kw",
#     "created_time": "2025-05-26T13:51:19+0000"
#   },
#   // ... más mensajes
# ]



# Message Details Schema
# {
#   "id": "string",
#   "created_time": "string",
#   "from": {
#     // Información del remitente
#   },
#   "to": {
#     "data": [
#       // Array de destinatarios
#     ]
#   },
#   "message": "string"
# }