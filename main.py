import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import os
from dotenv import load_dotenv
import schedule
import time


load_dotenv()
TOKEN = os.getenv("TOKEN")
# ADMIN_USER = "WinbuzzPromoter".strip()  # username of the admin user
ADMIN_USER = "manshi_rathour".strip()   # my personal user name for testing
CHAT_ID = os.getenv("CHAT_ID")  # Add your channel chat ID here


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
        /getchatid - to get the chat ID of the channel

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

    # Check if the message sender is the admin who initiated the advertising
    if user.username == advertising_user.username:
        # Save the advertising message
        context.user_data['advertising_message'] = update.message.text

        advertising_message = context.user_data['advertising_message']
        print(f"Advertising Message: {advertising_message}")

        # Inform the admin that the advertising message has been received
        update.message.reply_text(
            f"Advertising message received. It will be posted in the channels.\n\n"
            f"Advertising Message: {advertising_message}"
        )

        # Send the advertising message to all channels where the admin is an admin
        send_advertising_message_to_all_channels(TOKEN, advertising_message)

    else:
        update.message.reply_text("You are not authorized to provide the advertising message.")


def send_advertising_message_to_all_channels(bot_token, advertising_message):
    print(f"bot:{bot_token}, advertising_message: {advertising_message}")
    bot = telegram.Bot(token=bot_token)

    try:
        channels = get_all_channels(bot_token)  # Reuse the get_all_channels function

        if channels:
            for channel_id in channels:
                try:
                    bot.send_message(chat_id=channel_id, text=advertising_message, parse_mode=telegram.ParseMode.MARKDOWN)
                except telegram.error.TelegramError as e:
                    print(f"Error sending message to channel {channel_id}: {e}")
        else:
            print("The bot is not a member or administrator in any channels.")
    except Exception as e:
        print(f"Error sending messages to channels: {e}")


def get_all_channels(bot_token):

    bot = telegram.Bot(token=bot_token)
    channels = []

    try:
        # Use getUpdates with an offset for more efficient retrieval
        offset = 0
        while True:
            updates = bot.getUpdates(offset=offset)
            if not updates:
                break

            for update in updates:
                chat_id = update.message.chat_id
                chat_type = update.message.chat.type

                # Ensure it's a channel and the bot is a member or administrator
                if chat_type == 'channel' and chat_id not in channels:
                    chat_member = bot.get_chat_member(chat_id=chat_id, user_id=bot.get_me().id)
                    if chat_member.status in ["member", "administrator", "creator"]:
                        channels.append(chat_id)

            offset = max(update.update_id + 1, offset + 1)  # Update offset for next iteration

    except Exception as e:
        print(f"Error getting channels: {e}")

    print("Channels: ", channels)
    return channels





def get_chat_id(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(f"Chat ID: {chat_id}")


# Schedule the advertisement at 12 PM every day
schedule.every().day.at("12:00").do(advertise)

# Schedule the advertisement at 6 PM every day
schedule.every().day.at("18:00").do(advertise)

updater = telegram.ext.Updater(TOKEN, use_context=True)
dispatch = updater.dispatcher

dispatch.add_handler(telegram.ext.CommandHandler('start', start))
dispatch.add_handler(telegram.ext.CommandHandler('help', helps))
dispatch.add_handler(telegram.ext.CommandHandler('advertise', advertise))
dispatch.add_handler(telegram.ext.CommandHandler('getchatid', get_chat_id))


updater.start_polling()

while True:
    schedule.run_pending()
    time.sleep(1)

# The time.sleep(1) adds a short delay (1 second in this case) before the loop checks for scheduled tasks again.
