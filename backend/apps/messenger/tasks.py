# my_app/tasks.py
from .graphqlAPI import (
    get_conversations,
    get_messages,
    get_message_details
)
from django.conf import settings
import logging
from datetime import datetime
from .models import Conversation
from apps.comment_user_owner.models import UserOwner
from apps.comment.models import Comment
from apps.source.models import Source

logger = logging.getLogger(__name__)

FACEBOOK_PAGE_NAME = settings.FACEBOOK_PAGE_NAME

def messenger_api_task():
    logger.info("Executing messenger_api_task")

    conversations_data = get_conversations()  # Renombrado para claridad
    stop_loop_conversations = False  # Renombrado para claridad

    if not conversations_data or 'data' not in conversations_data:
        logger.error("No conversation data received or format is incorrect.")
        return

    for conv_api_data in conversations_data['data']:  # Iterar sobre los datos de la API

        conversation_api_id = conv_api_data['id']  # ID de la conversación desde la API

        # verificar el tiempo de actualizacion de esta conversacion que
        # sea mas reciente que le tiempo de actualizacion de la misma peticion en la base de datos,
        # si no lo es que pase a la siguiente conversacion.

        curr_conv = conv_api_data['updated_time']
        conversation = Conversation.objects.filter(messenger_id=conversation_api_id).first()

        if conversation:
            curr_conv_clean = curr_conv.split('+')[0]  # '2025-05-30T17:53:56'
            curr_dt = datetime.strptime(curr_conv_clean, "%Y-%m-%dT%H:%M:%S")

            # Fecha desde tu BD (ya está limpia)
            old_conv = conversation.messenger_updated_at.strftime("%Y-%m-%d %H:%M:%S")
            old_dt = datetime.strptime(old_conv, "%Y-%m-%d %H:%M:%S")

            # Comparar
            if curr_dt <= old_dt:
                continue

        messages_data = get_messages(conversation_api_id)  # Renombrado para claridad

        if not messages_data or 'messages' not in messages_data:
            logger.error(f"No messages data received or format is incorrect for conversation {conversation_api_id}.")
            continue  # Saltar a la siguiente conversación

        messages_api_list = messages_data['messages']['data']
        stop_loop_messages = False  # Bandera para este bucle de mensajes

        for i, message_api_data in enumerate(messages_api_list):  # Iterar sobre los datos de mensajes de la API
            # Verificar que el mensaje ya fue leido o no
            # si es el primer mensaje y ya fue leido entonces detener toda la revision
            # en caso de que el primero no sea leido continuar
            conversation = Conversation.objects.filter(messenger_id=conversation_api_id).first()

            if conversation:
                comment = Comment.objects.filter(
                    messenger_id=message_api_data['id'],
                    messenger_conversation__id=conversation.id
                ).first()

            else:
                comment = None

            # print(comment)
            if comment:
                logger.info(
                    f"Message API ID {message_api_data['id']} already exists in DB for conversation API ID {conversation_api_id}.")
                if i == 0:
                    # Si el mensaje ya fue guardado y es el primero (más reciente) de la lista de la API
                    stop_loop_conversations = True  # Indicamos que no se procesen más conversaciones
                    logger.info(
                        f"Most recent message for conversation API ID {conversation_api_id} already in DB. Stopping further conversation processing.")
                break  # Salir del bucle de mensajError processing messagees para esta conversación

            msg_details_api = get_message_details(message_api_data['id'])

            if not msg_details_api:
                logger.error(f"Could not get details for message API ID: {message_api_data['id']}")
                continue

            message_api_id = msg_details_api['id']
            message_content = msg_details_api['message']
            user_from = msg_details_api['from']['name']
            created_time = msg_details_api['created_time']

            # Esto verifica que solo se capturen mensajes de la otra persona
            # y no del propio perfil
            if user_from == FACEBOOK_PAGE_NAME:
                continue

            user = UserOwner.objects.filter(name=user_from).first()
            if not user:
                user = UserOwner.objects.create(
                    name=user_from
                )

            # Intentar obtener la conversación de la BD o crearla si no existe
            try:
                # Asumimos que tienes un campo único para el ID de la API en tu modelo Conversation
                # Por ejemplo: id_from_api = models.CharField(max_length=255, unique=True)
                # O si el 'id' de la API puede ser el PK de tu modelo Conversation si es un UUID o similar.
                # Aquí usaré 'id_messenger' como en tu ejemplo original para Message.
                # Ajusta 'id_messenger' al nombre real del campo en tu modelo Conversation
                # que almacena el ID de la conversación de la API.us

                conversation = Conversation.objects.filter(messenger_id=conversation_api_id).first()

                if not conversation:
                    conversation = Conversation.objects.create(
                        messenger_id=conversation_api_id,
                        link=conv_api_data['link'],
                        messenger_updated_at=conv_api_data['updated_time'],
                        user=user
                    )

                    logger.info(f"New conversation created in DB with API ID: {conversation_api_id}")


            except Exception as e:  # Captura cualquier error durante get_or_create
                logger.error(f"Error getting or creating conversation {conversation_api_id}: {e}")
                continue  # Saltar a la siguiente conversación de la API si hay un error aquí

            # Comprobar si el mensaje ya fue guardado
            try:
                source = Source.objects.filter(name="messenger").first()
                if not source:
                    source = Source.objects.create(
                        name='messenger',
                        description='Mensajes de Messenger',
                        url='https://messenger.com',
                        created_at=created_time
                    )

                conversation = Conversation.objects.filter(messenger_id=conversation_api_id).first()

                # Guardar el mensaje
                Comment.objects.create(
                    messenger_id=message_api_id,
                    text=message_content,
                    user=None,
                    user_owner=user,
                    post=None,
                    classification=None,
                    source=source,
                    messenger_conversation=conversation,
                    messenger_created_at=created_time
                )

                logger.info(
                    f"Message API ID {message_api_id} created in DB for conversation API ID {conversation_api_id}.")

            except Exception as e:  # Captura cualquier error durante la verificación o creación del mensaje
                logger.error(
                    f"Error processing message API ID {message_api_id} for conversation {conversation_api_id}: {e}")
                # Podrías decidir continuar con el siguiente mensaje o romper el bucle de mensajes
                # dependiendo de la severidad del error. Por ahora, continuamos.
                continue

        if stop_loop_conversations:
            break  # Salir del bucle de conversaciones

    logger.info("Finished fetching and storing API data.")

