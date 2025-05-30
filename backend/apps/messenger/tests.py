from django.test import TestCase

# Create your tests here.
import schedule
import time
import requests
from .graphqlAPI import  get_conversation_with_user , get_messages
def task_consult():
    """
    Esta función define la secuencia de acciones que se ejecutarán periódicamente.
    """
    print(f"--- Iniciando tarea periódica en: {time.ctime()} ---")

    # Ejemplo: Obtener conversación para un usuario específico
    user_id_ejemplo = "ID_DE_USUARIO_ESPECIFICO" # Reemplaza con un ID de usuario real o una lógica para obtenerlo
    conversation_data = get_conversation_with_user(user_id_ejemplo)

    if conversation_data and 'data' in conversation_data and conversation_data['data']:
        # Suponiendo que la API devuelve una lista de conversaciones y tomamos la primera
        conversation_id = conversation_data['data'][0]['id']
        print(f"Conversación obtenida: {conversation_id}")

        # Ahora, obtén los mensajes de esa conversación
        messages_data = get_messages(conversation_id)

        if messages_data and 'messages' in messages_data and 'data' in messages_data['messages']:
            print(f"Mensajes obtenidos para {conversation_id}: {len(messages_data['messages']['data'])} mensajes.")
            for message in messages_data['messages']['data']:
                message_id = message['id']
                # Opcionalmente, obtén detalles de cada mensaje
                # details = get_message_details(message_id)
                # if details:
                #     print(f"  Detalles del mensaje {message_id}: {details.get('message', 'N/A')}")
                print(f"  ID del Mensaje: {message_id}, Contenido: {message.get('message', 'N/A')}")
        else:
            print(f"No se encontraron mensajes o hubo un error para la conversación {conversation_id}")
    else:
        print(f"No se encontró conversación o hubo un error para el usuario {user_id_ejemplo}")
    print("--- Tarea periódica finalizada ---")

# --- 2. Programa la tarea ---
# Puedes elegir diferentes unidades de tiempo:
# schedule.every(10).minutes.do(mi_tarea_periodica)
# schedule.every().hour.do(mi_tarea_periodica)
# schedule.every().day.at("10:30").do(mi_tarea_periodica)
# schedule.every(5).to(10).minutes.do(mi_tarea_periodica)
# schedule.every().monday.do(mi_tarea_periodica)
# schedule.every().wednesday.at("13:15").do(mi_tarea_periodica)

# Para este ejemplo, la ejecutaremos cada 1 minuto.
# ¡Ajusta esto según tus necesidades! Podría ser demasiado frecuente para algunas APIs.

schedule.every(1).minutes.do(task_consult())

# --- 3. Ejecuta el programador ---
print("El programador de tareas ha iniciado. Presiona Ctrl+C para detener.")
try:
    while True:
        schedule.run_pending() # Ejecuta todas las tareas que están pendientes
        time.sleep(1)          # Espera 1 segundo antes de volver a comprobar
except KeyboardInterrupt:
    print("Programador detenido por el usuario.")