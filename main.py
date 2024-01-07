import telegram.ext
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
# print(TOKEN)


def start(update, context):
    update.message.reply_text("Hello! Welcome to TechnoPetal Bot.")


def helps(update, context):
    update.message.reply_text(
        """
        Hi there! I'm Telegram bot created by Manshi. Please follow these commands:
        /start - to start the conversation
        /help - to get help menu
        
        I hope this helps :) 
        """)


updater = telegram.ext.Updater(TOKEN, use_context=True)
dispatch = updater.dispatcher

dispatch.add_handler(telegram.ext.CommandHandler('start', start))
dispatch.add_handler(telegram.ext.CommandHandler('help', helps))

updater.start_polling()
updater.idle()
