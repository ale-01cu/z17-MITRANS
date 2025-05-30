from django.apps import AppConfig
import threading
import time
from apps.messenger.graphqlAPI import debug_graphqlAPI

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
        # Solo ejecutamos en el proceso de aplicación, no en el proceso de recarga
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            thread = threading.Thread(target=tarea_periodica, daemon=True)
            thread.name = "TareaPeriodica"
            thread.start()