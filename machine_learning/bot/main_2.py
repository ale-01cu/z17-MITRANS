from bot import Bot
import os

dirname = os.path.dirname(__file__)

messenger_template_path = os.path.join(dirname, 'templates/messenger_template.png')
messenger_template_2_path = os.path.join(dirname, 'templates/messenger_template_2.png')

def main():
    bot = Bot(
        name='MessengerBot',
        target_name='Messenger | Facebook',
        target_templates_paths=[
            messenger_template_path,
            messenger_template_2_path
        ]
    )
    bot.run()

if __name__ == "__main__":
    main()