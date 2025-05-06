from bot import Bot
import os
from db.db import engine, Base
import asyncio
import pyautogui
from config import RESOLUTIONS_AVILABLES

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

dirname = os.path.dirname(__file__)

messenger_template_path = os.path.join(dirname, 'templates/messenger_template(1920x1080).png')
messenger_request_msg_template_path = os.path.join(dirname, 'templates/messenger_request_message_template(1920x1080).png')
# messenger_template_path = os.path.join(dirname, 'templates/messenger_template(1360x768x100).png')
# messenger_request_msg_template_path = os.path.join(dirname, 'templates/messenger_request_message_template(1360x768x100).png')

def main():
    screen_width, screen_height = pyautogui.size()
    current_resolution = f"{screen_width}x{screen_height}"

    print(current_resolution)

    if current_resolution not in RESOLUTIONS_AVILABLES:
        raise Exception(f"La resolución actual {current_resolution} no está disponible. "
                        f"Las resoluciones disponibles son: {RESOLUTIONS_AVILABLES}")

    templates = []

    if current_resolution == '1920x1080':
        templates.append(os.path.join(dirname, 'templates/messenger_template(1920x1080).png'))
        templates.append(os.path.join(dirname, 'templates/messenger_request_message_template(1920x1080).png'))

    elif current_resolution == '1360x768':
        templates.append(os.path.join(dirname, 'templates/messenger_template(1360x768).png'))
        templates.append(os.path.join(dirname, 'templates/messenger_request_message_template(1360x768).png'))

    bot = Bot(
        name='MessengerBot',
        target_name='Messenger',
        target_templates_paths=templates,
        websocket_uri="ws://localhost:8000/ws/chat/sala1/bot/",
        display_resolution=current_resolution
    )
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()