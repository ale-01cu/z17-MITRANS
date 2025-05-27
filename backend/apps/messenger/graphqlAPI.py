from django.conf import settings
import requests

BASE_URL = settings.FACEBOOK_BASE_URL
PAGE_ID = settings.FACEBOOK_PAGE_ID
ACCESS_TOKEN = settings.FACEBOOK_ACCESS_TOKEN


def get_conversations(platform: str = "messenger"):
    """
    Obtiene todas las conversaciones de la página
    """
    url = f"{BASE_URL}/{PAGE_ID}/conversations"
    params = {
        "platform": platform,
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()


def get_conversation_with_user(user_id: str, platform: str = "messenger"):
    """
    Obtiene la conversación con un usuario específico
    """
    url = f"{BASE_URL}/{PAGE_ID}/conversations"
    params = {
        "platform": platform,
        "user_id": user_id,
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()


def get_messages(conversation_id: str):
    """
    Obtiene los mensajes de una conversación específica
    """
    url = f"{BASE_URL}/{conversation_id}"
    params = {
        "fields": "messages",
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()


def get_message_details(message_id: str):
    """
    Obtiene detalles de un mensaje específico
    """
    url = f"{BASE_URL}/{message_id}"
    params = {
        "fields": "id,created_time,from,to,message",
        "access_token": ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()


def debug_graphqlAPI():
    converstions = get_conversations()

    for conversation in converstions['data']:
        messages = get_messages(conversation_id=conversation['id'])
        messages = messages['messages']['data']

        for msg in messages:
            msg_detail = get_message_details(message_id=msg['id'])
            id = msg_detail['id']
            message = msg_detail['message']
            user_from = msg_detail['from']['name']
            users_to = msg_detail['to']['data']

            # print(f'Antes del bucle del print.')

            for user_to in users_to:
                user_to_name = user_to['name']
                print(f'Messages from {user_from} to {user_to_name} -> {message}')


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