from django.apps import AppConfig
import threading
import time
from apps.messenger.graphqlAPI import debug_graphqlAPI
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.core.signals import request_started

_thread = None

def tarea_periodica():
    while True:
        print("=== TAREA EJECUTÁNDOSE ===")
        try:
            debug_graphqlAPI()
        except Exception as e:
            print(f"Error al ejecutar debug_graphqlAPI: {str(e)}")
        time.sleep(300)  # Espera 300 segundos (5 minutos)

class StartupConfig(AppConfig):
    name = 'core'
    
    def ready(self):
        # Registramos el receptor de la señal
        request_started.connect(iniciar_tarea_periodica)

def iniciar_tarea_periodica(sender, **kwargs):
    global _thread
    if _thread is None:
        _thread = threading.Thread(target=tarea_periodica, daemon=True)
        _thread.name = "TareaPeriodica"
        _thread.start()
        print("=== Tarea periódica iniciada después del arranque del servidor ===")