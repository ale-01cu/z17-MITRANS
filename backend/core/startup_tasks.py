from django.apps import AppConfig
import threading
import time
import os
import logging

logger = logging.getLogger(__name__)


_thread = None

def tarea_periodica():
    from apps.messenger.tasks import messenger_api_task
    from apps.user.models import Entity

    while True:
        time.sleep(300)  # Espera 300 segundos (5 minutos)
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

                    logger.info(f"Ejecutando tarea de messenger_api_task para la entidad {entity.name}")

                    messenger_api_task(facebook_page_id=facebook_page_id,
                                       facebook_page_name=facebook_page_name,
                                       facebook_access_token=facebook_access_token,
                                       entity_name=entity.name)

        except Exception as e:
            print(f"Error al ejecutar messenger_api_task: {str(e)}")

class StartupConfig(AppConfig):
    name = 'core'
    
    # def ready(self):
    #     # Registramos el receptor de la señal
    #     request_started.connect(iniciar_tarea_periodica)
    if os.environ.get('RUN_MAIN') != 'true':
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