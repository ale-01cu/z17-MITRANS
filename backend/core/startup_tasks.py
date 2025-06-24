from django.apps import AppConfig
from django.conf import settings
import threading
import time
import os
import logging

logger = logging.getLogger(__name__)


_thread = None

def tarea_periodica():
    from apps.messenger.tasks import messenger_api_task, send_message_to_all_users, send_messsage_to_conversations_less_than_24h_task
    from apps.user.models import Entity

    while True:
        # Contador regresivo desde 5 minutos (300 segundos)
        for resting_minutes in range(5, 0, -1):
            logger.info(f"[TASKS] {resting_minutes} minutes until the next execution.")
            time.sleep(2)  # Dormir 60 segundos

        # Ejecutar la tarea principal
        logger.info("=== Executing Tasks ===")
        try:
            entities = Entity.objects.filter(is_active=True)
            for entity in entities:
                if not hasattr(entity, 'facebookpage'):
                    continue

                facebook_page = entity.facebookpage
                if facebook_page:
                    facebook_page_id = facebook_page.facebook_page_id
                    facebook_page_name = facebook_page.facebook_page_name
                    facebook_access_token = facebook_page.facebook_access_token

                    logger.info(f"Executing [messenger_api_task] task for entity {entity.name}.")

                    # send_message_to_all_users(
                    #     message_text="Hola, este es un mensaje de prueba.",
                    #     facebook_page_name=facebook_page_name,
                    #     facebook_access_token=facebook_access_token,
                    #     facebook_page_id=facebook_page_id,
                    # )

                    messenger_api_task(
                        facebook_page_id=facebook_page_id,
                        facebook_page_name=facebook_page_name,
                        facebook_access_token=facebook_access_token,
                        entity_name=entity.name
                    )

                    send_messsage_to_conversations_less_than_24h_task(
                        message_text=(
                            "Hola, su queja ha sido recibida y está en proceso. "
                            "Para completar el registro, por favor responda *exactamente* con el siguiente formato:\n\n"
                            "**Teléfono:** [su teléfono]\n"
                            "**Correo:** [su correo electrónico]\n"
                            "**Provincia:** [su provincia actual]\n\n"
                            "Ejemplo:\n"
                            "Teléfono: 5431254, Correo: test@example.com, Provincia: Habana\n\n"
                            "Puede poner o numero de teléfono o correo electrónico, ambos no son obligatorios."
                        ),
                        facebook_page_name=facebook_page_name,
                        facebook_access_token=facebook_access_token,
                        facebook_page_id=facebook_page_id,
                    )

        except Exception as e:
            logger.error(f"Error executing messenger_api_task: {str(e)}", exc_info=True)

class StartupConfig(AppConfig):
    name = 'core'
    
    # def ready(self):
    #     # Registramos el receptor de la señal
    #     request_started.connect(iniciar_tarea_periodica)
    can_run_taks = settings.RUN_TASKS
    if os.environ.get('RUN_MAIN') != 'true' and can_run_taks == 'True':
        thread = threading.Thread(target=tarea_periodica, daemon=True)
        thread.name = "TareaPeriodica"
        thread.start()


def iniciar_tarea_periodica(sender, **kwargs):
    global _thread
    if _thread is None:
        _thread = threading.Thread(target=tarea_periodica, daemon=True)
        _thread.name = "TareaPeriodica"
        _thread.start()
        print("=== Tarea periódica iniciada después del arranque del servidor ===")