import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
import os
import threading


load_dotenv()
TOKEN = os.getenv("TOKEN")

# List of allowed admin usernames

# ALLOWED_ADMINS = ["manshi_rathour", "WinbuzzPromoter" ]
ALLOWED_ADMINS = ["manshi_rathour","precise12"]   # my personal user name for testing

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


# Use context.user_data to store user progress
def advertise(update, context):
    user = update.message.from_user

    # Check if the user sending the command is the admin user
    if user.username in ALLOWED_ADMINS:
        update.message.reply_text(
            "Send the post that you want to advertise in the channels where you are an admin.")

        # Set the initial state
        context.user_data['state'] = 'waiting_message'

    else:
        update.message.reply_text("You are not authorized to use this command.")
        return


def handle_user_input(update, context):
    # Check if the message has text or caption
    if update.message.text:
        user_input = update.message.text.strip()
    elif update.message.caption:
        user_input = update.message.caption.strip()
    else:
        update.message.reply_text("Invalid message type. Please send a valid text or caption.")
        return

    if context.user_data.get('state') == 'waiting_message':
        # Save the advertising message
        context.user_data['advertising_message'] = update.message
        context.user_data['state'] = 'waiting_choice'

        # Ask the user if they want to send the message immediately or schedule it
        keyboard = [
            ["send now", "schedule later"]
        ]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text("Advertising message received. Do you want to send it now or schedule it for later?",
                                  reply_markup=reply_markup)

    elif context.user_data.get('state') == 'waiting_choice':
        choice = user_input.lower()
        if choice == "send now":
            send_advertising_message_to_all_channels(context)
            update.message.reply_text("The advertising message has been sent.")
        elif choice == "schedule later":
            update.message.reply_text(
                "Please specify the time to schedule the message (in HH:MM format, 24-hour clock).")

            # Change the state to 'waiting_schedule'
            context.user_data['state'] = 'waiting_schedule'
        else:
            update.message.reply_text("Invalid choice. Please choose 'Send Now' or 'Schedule Later.'")

    elif context.user_data.get('state') == 'waiting_schedule':
        scheduled_time_str = user_input

        try:
            local_tz = pytz.timezone('Asia/Kolkata')  # Set the local time zone (India Standard Time)

            # Set the date to today and parse the time
            current_date = datetime.now(local_tz).date()
            scheduled_time = local_tz.localize(
                datetime.strptime(f"{current_date} {scheduled_time_str}", "%Y-%m-%d %H:%M"))

            current_time = datetime.now(local_tz)
            print("current time:", current_time)
            print('schedule time', scheduled_time)

            if scheduled_time > current_time:
                # Schedule the job using threading
                delta = scheduled_time - current_time
                threading.Timer(delta.total_seconds(), send_advertising_message_to_all_channels, [context]).start()
                update.message.reply_text(
                    f"The advertising message is scheduled to be sent at {scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.")
            else:
                update.message.reply_text("Invalid time. Please specify a time in the future.")
        except ValueError:
            update.message.reply_text("Invalid time format. Please use HH:MM format (24-hour clock).")


def send_advertising_message_to_all_channels(context):
    advertising_message = context.user_data.get('advertising_message')

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


# Create the MessageHandler to handle user input
advertise_handler = MessageHandler(Filters.all & ~Filters.command, handle_user_input)

# Create the Updater and add the handlers
updater = telegram.ext.Updater(TOKEN, use_context=True)
dispatch = updater.dispatcher
dispatch.add_handler(CommandHandler('advertise', advertise))
dispatch.add_handler(advertise_handler)

dispatch.add_handler(telegram.ext.CommandHandler('start', start))
dispatch.add_handler(telegram.ext.CommandHandler('help', helps))

# Start the Bot
updater.start_polling()
updater.idle()
