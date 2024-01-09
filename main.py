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
# ADMIN_USER = "WinbuzzPromoter".strip()  # username of the admin user
ADMIN_USER = "manshi_rathour".strip()   # my personal user name for testing
CHAT_ID = os.getenv("CHAT_ID")  # Add your channel chat ID here
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
    print(f"User: {user}")
    print(f"Admin User: {ADMIN_USER}")
    print(f"User ID: {user.id}")
    print(f"User Username: {user.username}")

    # Check if the user sending the command is the admin user
    if user.username == ADMIN_USER:

        update.message.reply_text(
            "Send the post that you want to advertise in the channels where you are an admin.")

        # Add a new handler to capture the admin's advertising message
        context.user_data['advertising_user'] = user
        context.user_data['advertising_message'] = None

        # Use the MessageHandler to register the advertising message handler
        message_handler = MessageHandler(Filters.text & ~Filters.command, advertising_message_handler)
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
        context.user_data['advertising_message'] = update.message.text

        advertising_message = context.user_data['advertising_message']
        print(f"Advertising Message: {advertising_message}")

        # Inform the admin that the advertising message has been received
        update.message.reply_text(
            f"Advertising message received. It will be posted in the channels.\n\n"
            f"Advertising Message:\n {advertising_message}"
        )

        # Send the advertising message to all channels where you are admin
        send_advertising_message_to_all_channels(context)

    else:
        update.message.reply_text("You are not authorized to provide the advertising message.")


def send_advertising_message_to_all_channels(context):
    admin_username = context.user_data['advertising_user'].username
    advertising_message = context.user_data['advertising_message']

    if CHAT_ID:
        # Convert the string of chat IDs to a list of integers
        chat_ids = [int(chat_id) for chat_id in CHAT_ID.split(',')]

        for chat_id in chat_ids:
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            params = {
                'chat_id': chat_id,
                'text': advertising_message
            }
            response = requests.post(url, data=params)
            print(response.json())


# Schedule the advertisement at 12 PM every day
schedule.every().day.at("12:00").do(advertise)

# Schedule the advertisement at 6 PM every day
schedule.every().day.at("18:00").do(advertise)

updater = telegram.ext.Updater(TOKEN, use_context=True)
dispatch = updater.dispatcher

dispatch.add_handler(telegram.ext.CommandHandler('start', start))
dispatch.add_handler(telegram.ext.CommandHandler('help', helps))
dispatch.add_handler(telegram.ext.CommandHandler('advertise', advertise))


updater.start_polling()
updater.idle()
