from django.shortcuts import render

# Create your views here.
# class GetLastMessages():

# views.py o archivo donde esté tu función
from django.core.exceptions import ObjectDoesNotExist
from .models import Message,LastProcessedMessage
from .graphqlAPI import get_conversations,get_messages,get_message_details


def debug_graphqlAPI():
    try:
        # Obtiene el último mensaje procesado
        last_processed = LastProcessedMessage.objects.get(id=1)
        last_id = last_processed.last_message_id
    except ObjectDoesNotExist:
        # Si no existe, inicia con None
        last_id = None

    new_last_id = last_id  # Almacena el nuevo ID máximo

    conversations = get_conversations()

    for conversation in conversations['data']:
        messages = get_messages(conversation_id=conversation['id'])
        messages = messages['messages']['data']

        for msg in messages:
            msg_detail = get_message_details(message_id=msg['id'])
            current_id = msg_detail['id']

            # Si el mensaje ya fue procesado, saltarlo
            if last_id and current_id <= last_id:
                continue

            # Procesa el mensaje (guardar en DB, imprimir, etc.)
            message = msg_detail['message']
            user_from = msg_detail['from']['name']
            users_to = msg_detail['to']['data']

            # Guarda en la base de datos
            Message.objects.create(
                message_id=current_id,
                content=message,
                sender=user_from
            )

            # Actualiza el nuevo ID máximo si es necesario
            if new_last_id is None or current_id > new_last_id:
                new_last_id = current_id

            # Imprime detalles
            print('Antes del bucle del print.')
            for user_to in users_to:
                print(f'Messages from {user_from} to {user_to["name"]} -> {message}')

    # Actualiza el último mensaje procesado si hay nuevos
    if new_last_id != last_id:
        LastProcessedMessage.objects.update_or_create(
            id=1,
            defaults={'last_message_id': new_last_id}
        )