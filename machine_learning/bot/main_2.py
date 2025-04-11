from bot import Bot
import os
from db.db import engine, Base
import asyncio

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

dirname = os.path.dirname(__file__)

messenger_template_path = os.path.join(dirname, 'templates/messenger_template.png')
# messenger_template_2_path = os.path.join(dirname, 'templates/messenger_template_2.png')

def main():
    bot = Bot(
        name='MessengerBot',
        target_name='Messenger | Facebook',
        target_templates_paths=[
            messenger_template_path,
            # messenger_template_2_path
        ],
        websocket_uri="ws://localhost:8000/ws/chat/sala1/bot/"
    )
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()