from bot_module import Bot
import os
from db.db import engine, Base
import asyncio
import pyautogui
from config import RESOLUTIONS_AVILABLES, config_logger
import logging

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

dirname = os.path.dirname(__file__)

messenger_template_path = os.path.join(dirname, 'templates/messenger_template(1920x1080).png')
messenger_request_msg_template_path = os.path.join(dirname, 'templates/messenger_request_message_template(1920x1080).png')
# messenger_template_path = os.path.join(dirname, 'templates/messenger_template(1360x768).png')
# messenger_request_msg_template_path = os.path.join(dirname, 'templates/messenger_request_message_template(1360x768x100).png')

def main():
    screen_width, screen_height = pyautogui.size()
    current_resolution = f"{screen_width}x{screen_height}"

    print("Current Resolution: ", current_resolution)

    if current_resolution not in RESOLUTIONS_AVILABLES:
        raise Exception(f"La resolución actual {current_resolution} no está disponible. "
                        f"Las resoluciones disponibles son: {RESOLUTIONS_AVILABLES}")

    templates = []

    if current_resolution == '1920x1080':
        templates.append(os.path.join(dirname, 'templates/messenger_template(1920x1080).png'))
        # templates.append(os.path.join(dirname, 'templates/messenger_template_2(1920x1080).png'))
        templates.append(os.path.join(dirname, 'templates/messenger_request_message_template(1920x1080).png'))

    elif current_resolution == '1360x768':
        templates.append(os.path.join(dirname, 'templates/messenger_template(1360x768).png'))
        # templates.append(os.path.join(dirname, 'templates/messenger_template_2(1360x768).png'))
        templates.append(os.path.join(dirname, 'templates/messenger_request_message_template(1360x768).png'))

    logger = config_logger(
        nombre_logger='MessengerBot',
        nombre_fichero_log='log_messenger_bot.log',
        nivel_log=logging.DEBUG,  # Captura desde mensajes DEBUG hacia arriba
        directorio_logs='logs'
    )

    bot = Bot(
        name='MessengerBot',
        target_name='Messenger',
        target_templates_paths=templates,
        logger=logger,
        websocket_uri="ws://localhost:8000/ws/chat/sala1/bot/",
        display_resolution=current_resolution
    )
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()