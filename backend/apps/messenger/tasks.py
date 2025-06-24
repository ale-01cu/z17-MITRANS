# my_app/tasks.py
from .graphqlAPI import FacebookAPIGraphql
from django.conf import settings
import logging
from datetime import datetime
from .models import Conversation
from apps.comment_user_owner.models import UserOwner
from apps.comment.models import Comment
from apps.source.models import Source
from apps.user.models import Entity
from apps.classification.ml.model_loader import predict_comment_label
from apps.classification.models import Classification
from .utils import validate_answer_format_and_extract
from datetime import timedelta
from django.utils import timezone  # Import correcto

logger = logging.getLogger(__name__)

FACEBOOK_PAGE_NAME = settings.FACEBOOK_PAGE_NAME
LIMIT_MESSAGES = settings.MESSAGES_PEER_CONVERSATION_IN_NEW_CONVERSATION

def messenger_api_task(facebook_page_name: str = None,
                       facebook_access_token: str = None,
                       facebook_page_id: str = None,
                       entity_name: str = None):
    logger.info(f"Executing [messenger_api_task] task for entity {entity_name} and page {facebook_page_name}")

    apiGql = FacebookAPIGraphql(facebook_page_name,
                                    facebook_access_token,
                                    facebook_page_id)

    conversations_data = apiGql.get_conversations()  # Renombrado para claridad
    stop_loop_conversations = False  # Renombrado para claridad

    if not conversations_data or 'data' not in conversations_data:
        logger.error("No conversation data received or format is incorrect.")
        return

    for conv_api_data in conversations_data['data'][::-1]:  # Iterar sobre los datos de la API
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

        messages_data = apiGql.get_messages(conversation_api_id)  # Renombrado para claridad

        if not messages_data or 'messages' not in messages_data or 'data' not in messages_data['messages']:
            logger.error(f"No messages data received or format is incorrect for conversation {conversation_api_id}.")
            continue  # Saltar a la siguiente conversación

        messages_api_list = messages_data['messages']['data']
        stop_loop_messages = False  # Bandera para este bucle de mensajes

        if not conversation:
            messages_api_list = messages_api_list[:LIMIT_MESSAGES]

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

            msg_details_api = apiGql.get_message_details(message_api_data['id'])

            if not msg_details_api:
                logger.error(f"Could not get details for message API ID: {message_api_data['id']}")
                continue

            message_api_id = msg_details_api['id']
            message_content = msg_details_api['message']
            user_from_id = msg_details_api['from']['id']
            user_from_name = msg_details_api['from']['name']
            created_time = msg_details_api['created_time']

            # Esto verifica que solo se capturen mensajes de la otra persona
            # y no del propio perfil
            if user_from_name == FACEBOOK_PAGE_NAME:
                continue

            user = UserOwner.objects.filter(name=user_from_name).first()

            if not user:
                user = UserOwner.objects.create(
                    name=user_from_name,
                    facebook_id=user_from_id
                )

            # ============================================= Check User Response for extract data ======================================================
            # This bool is for knows when analize the message or not on base
            # a conversation was answered or not by the system
            can_extract_user_data_from_message = (
                    conversation
                    and conversation.is_answer_sent
                    and not conversation.is_user_reply_received
                    and conversation.last_answer_date_sent  # Aseguramos que no sea None
                    and (timezone.now() - conversation.last_answer_date_sent) < timedelta(hours=72)
            )

            if can_extract_user_data_from_message:
                is_ok, data = validate_answer_format_and_extract(user_answer=message_content)

                if is_ok:
                    phone = data['phone']
                    email = data['email']
                    province = data['province']

                    user.phone_number = phone
                    user.email = email
                    user.province = province
                    user.save()

                    conversation.is_user_reply_received = True
                    conversation.save()
            # ============================================= Check User Response for extract data ======================================================

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

                label = predict_comment_label(comment=message_content)

                classification = Classification.objects.filter(name=label).first()

                if not classification:
                    classification = Classification.objects.create(
                        name=label,
                        description=f"Etiqueta generada automáticamente para el comentario '{message_content}'",
                    )

                conversation = Conversation.objects.filter(messenger_id=conversation_api_id).first()
                entity = Entity.objects.filter(name=entity_name).first()

                # Guardar el mensaje
                Comment.objects.create(
                    messenger_id=message_api_id,
                    text=message_content,
                    user=None,
                    user_owner=user,
                    entity=entity,
                    post=None,
                    classification=classification,
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

    logger.info(f"Finished [messenger_api_task] task for entity {entity_name}.")


def send_messsage_to_conversations_less_than_24h_task(
        message_text: str = None,
        facebook_page_name: str = None,
        facebook_access_token: str = None,
        facebook_page_id: str = None,
) -> None:
    """
    Send message to conversations that were created less than 24 hours ago

    """
    can_answer = settings.CAN_ANSWER
    if not can_answer == 'True':
        return


    logger.info("Executing [send_messsage_to_conversations_less_than_24h_task] task.")


    apiGql = FacebookAPIGraphql(facebook_page_name,
                                facebook_access_token,
                                facebook_page_id)


    hace_24_horas = timezone.now() - timedelta(hours=24)
    conversations = Conversation.objects.filter(is_answer_sent=False,
                                                is_user_reply_received=False)

    for conversation in conversations:
        last_message = (Comment.objects
            .filter(
                messenger_conversation=conversation,  # Filtramos por conversación
                messenger_created_at__gte=hace_24_horas,  # Solo mensajes de las últimas 24h
            )
            .order_by('-messenger_created_at')  # Ordena por fecha descendente
            .exists()
         )

        if not last_message:
            continue

        response = apiGql.send_text_message(
            message_text=message_text,
            psid=conversation.user.facebook_id
        )

        if response:
            conversation.is_answer_sent = True
            conversation.last_answer_date_sent = timezone.now()
            conversation.save()

    conversations = Conversation.objects.filter(is_answer_sent=True,
                                                is_user_reply_received=True,
                                                is_final_answer_sent=False)

    for conversation in conversations:
        response = apiGql.send_text_message(
            message_text="Muchas gracias por su tiempo. Sus quejas estan siendo procesadas.",
            psid=conversation.user.facebook_id
        )

        if response:
            conversation.is_final_answer_sent = True
            conversation.save()


    logger.info(f"Finished [send_messsage_to_conversations_less_than_24h_task] task.")



def send_message_to_all_users(
                       message_text: str = None,
                       facebook_page_name: str = None,
                       facebook_access_token: str = None,
                       facebook_page_id: str = None,
):
    apiGql = FacebookAPIGraphql(facebook_page_name,
                                facebook_access_token,
                                facebook_page_id)

    users = UserOwner.objects.all()

    for user in users:
        user_name = user.name

        response = apiGql.send_text_message(message_text=message_text,
                                 psid=user.facebook_id)

        print(f"User {user_name} response {response}")
