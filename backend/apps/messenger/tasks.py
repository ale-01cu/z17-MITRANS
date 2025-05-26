# my_app/tasks.py
from celery import shared_task
from .graphqlAPI import (
    get_conversations,
    get_messages,
    get_message_details
)
from .models import Conversation, Message
from apps.comment_user_owner.models import UserOwner
from django.conf import settings

FACEBOOK_PAGE_NAME = settings.FACEBOOK_PAGE_NAME

@shared_task
def fetch_and_store_api_data():
    conversations_data = get_conversations()  # Renombrado para claridad
    stop_loop_conversations = False  # Renombrado para claridad

    if not conversations_data or 'data' not in conversations_data:
        print("No conversation data received or format is incorrect.")
        return

    for conv_api_data in conversations_data['data']:  # Iterar sobre los datos de la API
        conversation_api_id = conv_api_data['id']  # ID de la conversación desde la API

        messages_data = get_messages(conversation_api_id)  # Renombrado para claridad

        if not messages_data or 'data' not in messages_data:
            print(f"No messages data received or format is incorrect for conversation {conversation_api_id}.")
            continue  # Saltar a la siguiente conversación

        messages_api_list = messages_data['data']
        stop_loop_messages = False  # Bandera para este bucle de mensajes

        for i, message_api_data in enumerate(messages_api_list):  # Iterar sobre los datos de mensajes de la API
            msg_details_api = get_message_details(message_api_data['id'])

            if not msg_details_api:
                print(f"Could not get details for message API ID: {message_api_data['id']}")
                continue

            message_api_id = msg_details_api['id']
            message_content = msg_details_api['message']
            user_from = msg_details_api['from']['name']
            created_time = msg_details_api['created_time']

            if user_from == FACEBOOK_PAGE_NAME:
                continue

            user, created = UserOwner.objects.get_or_create(
                name=user_from,
                defaults={
                    'name': user_from,
                }
            )

            # Intentar obtener la conversación de la BD o crearla si no existe
            try:
                # Asumimos que tienes un campo único para el ID de la API en tu modelo Conversation
                # Por ejemplo: id_from_api = models.CharField(max_length=255, unique=True)
                # O si el 'id' de la API puede ser el PK de tu modelo Conversation si es un UUID o similar.
                # Aquí usaré 'id_messenger' como en tu ejemplo original para Message.
                # Ajusta 'id_messenger' al nombre real del campo en tu modelo Conversation
                # que almacena el ID de la conversación de la API.us

                conversation_db, created = Conversation.objects.get_or_create(
                    id_messenger=conversation_api_id,
                    defaults={
                        'user': user,
                        'link': conv_api_data['link'],
                        'updated_time': conv_api_data['updated_time']
                        # Aquí puedes añadir otros campos que quieras guardar al crear la conversación
                        # por primera vez, si la API los provee en `conv_api_data`.
                        # Ejemplo: 'name': conv_api_data.get('name', 'Default Conversation Name')
                    }
                )
                if created:
                    print(f"New conversation created in DB with API ID: {conversation_api_id}")

            except Exception as e:  # Captura cualquier error durante get_or_create
                print(f"Error getting or creating conversation {conversation_api_id}: {e}")
                continue  # Saltar a la siguiente conversación de la API si hay un error aquí

            # Comprobar si el mensaje ya fue guardado
            try:
                # Usamos filter().exists() que es más eficiente para solo verificar existencia
                message_exists_in_db = Message.objects.filter(
                    conversation=conversation_db,
                    id_messenger=message_api_id
                ).exists()

                if message_exists_in_db:
                    print(
                        f"Message API ID {message_api_id} already exists in DB for conversation API ID {conversation_api_id}.")
                    # Si el mensaje ya fue guardado y es el primero (más reciente) de la lista de la API
                    if i == 0:
                        stop_loop_conversations = True  # Indicamos que no se procesen más conversaciones
                        print(
                            f"Most recent message for conversation API ID {conversation_api_id} already in DB. Stopping further conversation processing.")
                    stop_loop_messages = True  # Dejar de procesar mensajes para ESTA conversación
                    break  # Salir del bucle de mensajes para esta conversación

                # Si el mensaje no existe, lo creamos
                Message.objects.create(
                    conversation=conversation_db,
                    id_messenger=message_api_id,  # Guardamos el ID del mensaje de la API
                    sender=user,
                    content=message_content,
                    created_time=created_time
                    # Asegúrate de que `created_time` sea un objeto datetime válido o conviértelo
                )
                print(f"Message API ID {message_api_id} created in DB for conversation API ID {conversation_api_id}.")

            except Exception as e:  # Captura cualquier error durante la verificación o creación del mensaje
                print(f"Error processing message API ID {message_api_id} for conversation {conversation_api_id}: {e}")
                # Podrías decidir continuar con el siguiente mensaje o romper el bucle de mensajes
                # dependiendo de la severidad del error. Por ahora, continuamos.
                continue

        if stop_loop_conversations:
            break  # Salir del bucle de conversaciones

    print("Finished fetching and storing API data.")
