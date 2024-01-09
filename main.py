import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import os
from dotenv import load_dotenv
import schedule
import time
import requests


load_dotenv()
TOKEN = os.getenv("TOKEN")

# List of allowed admin usernames

# ALLOWED_ADMINS = ["manshi_rathour", "WinbuzzPromoter" ]
ALLOWED_ADMINS = ["manshi_rathour"]   # my personal user name for testing

# update your chat id for every channel or groups in .env file
# you can follow steps to extract chat id from "to_extract_chat_id" file

CHAT_ID = os.getenv("CHAT_ID")
# print(CHAT_ID)
bot = telegram.Bot(token=TOKEN)
# print(bot)


def start(update, context):
    update.message.reply_text(
        "Hello! Welcome to TechnoPetal Bot.\nPlease write command: /help - to get help menu")


def helps(update, context):
    update.message.reply_text(
        """
        Hi there! I'm Telegram bot. Please follow these commands:
        /start - to start the conversation
        /help - to get help menu
        /advertise - to send an advertising post

        I hope this helps :)
        """)


def advertise(update, context):
    user = update.message.from_user
    print(f"Allowed Admins: {ALLOWED_ADMINS}")
    print(f"User: {user}")
    print(f"User ID: {user.id}")
    print(f"User Username: {user.username}")

    # Check if the user sending the command is the admin user
    if user.username in ALLOWED_ADMINS:

        update.message.reply_text(
            "Send the post that you want to advertise in the channels where you are an admin.")

        # Add a new handler to capture the admin's advertising message
        context.user_data['advertising_user'] = user
        context.user_data['advertising_message'] = None

        # Add a new handler to capture the admin's advertising message
        message_handler = MessageHandler(
            Filters.text | Filters.photo | Filters.video & ~Filters.command, advertising_message_handler)
        context.dispatcher.add_handler(message_handler)

    else:
        update.message.reply_text("You are not authorized to use this command.")


def advertising_message_handler(update, context):
    user = update.message.from_user
    advertising_user = context.user_data['advertising_user']

    print("Advertisement User: ", advertising_user)

    # Check if the message sender is the admin who initiated the advertising
    if user.username == advertising_user.username:
        # Save the advertising message
        context.user_data['advertising_message'] = update.message

        advertising_message = context.user_data['advertising_message']
        print(f"Advertising Message: {advertising_message}")

        # Inform the admin that the advertising message has been received
        update.message.reply_text(
            f"Advertising message received. It will be posted in the channels.")

        # Send the advertising message to all channels where you are admin
        send_advertising_message_to_all_channels(context)

    else:
        update.message.reply_text("You are not authorized to provide the advertising message.")


def send_advertising_message_to_all_channels(context):
    admin_username = context.user_data['advertising_user'].username
    advertising_message = context.user_data['advertising_message']

    if CHAT_ID:
        chat_ids = [int(chat_id) for chat_id in CHAT_ID.split(',')]

        for chat_id in chat_ids:
            # Check the type of media and send accordingly
            if advertising_message.text:
                # Text message
                text_params = {
                    'chat_id': chat_id,
                    'text': advertising_message.text
                }
                response = requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=text_params)
                print(response.json())
            elif advertising_message.photo:
                # Photo
                photo_params = {
                    'chat_id': chat_id,
                    'photo': advertising_message.photo[-1].file_id,
                    'caption': advertising_message.caption if advertising_message.caption else ""
                }
                response = requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendPhoto', data=photo_params)
                print(response.json())
            elif advertising_message.video:
                # Video
                video_params = {
                    'chat_id': chat_id,
                    'video': advertising_message.video.file_id,
                    'caption': advertising_message.caption if advertising_message.caption else ""
                }
                response = requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendVideo', data=video_params)
                print(response.json())


updater = telegram.ext.Updater(TOKEN, use_context=True)
dispatch = updater.dispatcher

dispatch.add_handler(telegram.ext.CommandHandler('start', start))
dispatch.add_handler(telegram.ext.CommandHandler('help', helps))
dispatch.add_handler(telegram.ext.CommandHandler('advertise', advertise))


updater.start_polling()
updater.idle()
