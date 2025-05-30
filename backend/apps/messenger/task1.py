import time
import threading
# Descomenta la siguiente línea si tu tarea necesita interactuar con la base de datos.
# from django.db import close_old_connections

def my_periodic_task():
    """
    Esta es la función que se ejecutará en el hilo de fondo.
    Imprime un mensaje cada 5 segundos.
    """
    # Obtenemos el nombre del hilo actual para incluirlo en los mensajes de log.
    # Esto es útil para depurar y entender qué está sucediendo.
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Iniciando ciclo de la tarea periódica.")

    while True:
        # Mensaje que se imprimirá periódicamente.
        print(f"[{thread_name}] Tarea periódica ejecutándose...")

        # --- INICIO: Lógica de tu tarea específica ---
        # Aquí es donde colocarías el código que quieres que se ejecute periódicamente.
        # Por ejemplo:
        # - Consultar una API externa.
        # - Realizar cálculos.
        # - Limpiar datos temporales.
        # - Si necesitas interactuar con la base de datos de Django,
        #   es una buena práctica envolver las operaciones de BD con close_old_connections:
        #
        # try:
        #     close_old_connections() # Cierra conexiones antiguas antes de usar la BD.
        #     # Ejemplo: count = YourModel.objects.count()
        #     # print(f"[{thread_name}] Hay {count} objetos en YourModel.")
        # finally:
        #     close_old_connections() # Cierra conexiones después de usar la BD.
        #
        # --- FIN: Lógica de tu tarea específica ---

        # Espera 5 segundos antes de la siguiente ejecución.
        time.sleep(5)