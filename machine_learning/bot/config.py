import logging
import os
import sys # Para sys.stdout en StreamHandler

RESOLUTIONS_AVILABLES = [
    '1920x1080',
    '1360x768',
]


BOT_CONFIG = {
    "1920x1080": {
        "FIRST_CONTOUR_REFERENCE": (534, 913, 518, 45),
        "FIND_CHATS_REFERENCE": {
            'min_width': 12,
            'max_width': 20,
            'min_height': 12,
            'max_height': 20,
        },
        "FIND_TEXT_AREA_CONTOURS": {
            'chat_limit_x_porcent': 0.6,
            'chat_start_x_porcent': 0.3,
            'chat_limit_x_porcent_in_message_requests_view': 0.5,
            'min_height': 40,
        },
        "GET_TEXTS_DID_NOT_WATCHED": {
            'x_start_offset': 10,
            'y_start_offset': 0,
            'scroll_move': 35,
            'min_height_text_location': 50,
            'max_height_text_location': 40,
        },
        "REVIEW_CHAT": {
            'scroll_move': 45,
        },
        "FIND_CURRENT_CHAT_ID": {
            'roi_x_start_porcent': 0.285,
        },
        "EXTRACT_CHAT_ID": {
            'y_sub': 25,
            'y_plus': 10,
            'x_sub': 313
        },
    },
    "1360x768": {
        "FIRST_CONTOUR_REFERENCE": (427, 634, 468, 36),
        "FIND_CHATS_REFERENCE": {
            'min_width': 10,
            'max_width': 20,
            'min_height': 10,
            'max_height': 20,
        },
        "FIND_TEXT_AREA_CONTOURS": {
            'chat_limit_x_porcent': 1,
            'chat_start_x_porcent': 0.4,
            'chat_limit_x_porcent_in_message_requests_view': 0.30,
            'min_height': 20,
        },
        "GET_TEXTS_DID_NOT_WATCHED": {
            'x_start_offset': 10,
            'y_start_offset': 10,
            'scroll_move': 25,
            'min_height_text_location': 45,
            'max_height_text_location': 35,
        },
        "REVIEW_CHAT": {
            'scroll_move': 35,
        },
        "FIND_CURRENT_CHAT_ID": {
            'roi_x_start_porcent': 0.32,
        },
        "EXTRACT_CHAT_ID": {
            'y_sub': 12,
            'y_plus': 10,
            'x_sub': 240
        },
    }
}


def config_logger(nombre_logger='mi_app',
                      nombre_fichero_log='app.log',
                      nivel_log=logging.INFO,
                      directorio_logs='logs'):
    """
    Configura un logger para imprimir en consola y guardar en un fichero.

    Args:
        nombre_logger (str): Nombre para el logger. Útil si tienes múltiples loggers.
        nombre_fichero_log (str): Nombre del fichero donde se guardarán los logs.
        nivel_log (int): Nivel mínimo de los mensajes a registrar (e.g., logging.DEBUG, logging.INFO).
        directorio_logs (str): Subdirectorio donde se guardará el fichero de log. Se creará si no existe.

    Returns:
        logging.Logger: El logger configurado.
    """
    # Crear el logger
    logger = logging.getLogger(nombre_logger)
    logger.setLevel(nivel_log)  # Establece el nivel mínimo para el logger

    # Evitar añadir manejadores múltiples si la función se llama varias veces
    # para el mismo nombre de logger.
    if logger.hasHandlers():
        logger.handlers.clear()

    # Crear el directorio de logs si no existe
    if not os.path.exists(directorio_logs):
        os.makedirs(directorio_logs)
        print(f"Directorio de logs creado: {os.path.abspath(directorio_logs)}")

    ruta_fichero_log = os.path.join(directorio_logs, nombre_fichero_log)

    # --- Formateador ---
    # Define el formato de los mensajes de log
    # %(asctime)s: Fecha y hora del log.
    # %(name)s: Nombre del logger.
    # %(levelname)s: Nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    # %(message)s: El mensaje de log.
    # %(module)s: Módulo donde se originó el log.
    # %(funcName)s: Función donde se originó el log.
    # %(lineno)d: Línea donde se originó el log.
    formato_log = '%(asctime)s - %(name)s - [%(levelname)s] - (%(module)s:%(funcName)s:%(lineno)d) - %(message)s'
    formatter = logging.Formatter(formato_log, datefmt='%Y-%m-%d %H:%M:%S')

    # --- Manejador para la Consola (StreamHandler) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(nivel_log)  # Nivel para este manejador específico
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- Manejador para el Fichero (FileHandler) ---
    # 'a' para append (añadir), 'w' para write (sobrescribir cada vez)
    file_handler = logging.FileHandler(ruta_fichero_log, mode='a', encoding='utf-8')
    file_handler.setLevel(nivel_log)  # Nivel para este manejador específico
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logger '{nombre_logger}' configurado. Logs se guardarán en: {os.path.abspath(ruta_fichero_log)}")
    return logger