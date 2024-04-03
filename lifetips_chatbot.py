from asyncore import dispatcher_with_send
import os
import logging
from httpx import QueryParams
import redis
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters, JobQueue
from datetime import timedelta
from chatbot import ChatbotAssistant
import bot_config

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Redis connection
redis_client = redis.Redis(host=bot_config.REDIS_HOST, port= bot_config.REDIS_PORT, password=bot_config.REDIS_PASSWORD)

# Initialize Chatbot Assistant
chatbot_assistant = ChatbotAssistant()

def send_chatbot_reply(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    life_tips_prompt = f"Providing life tips: {user_message}"
    try:
        reply_message = chatbot_assistant.submit(life_tips_prompt)
    except Exception as error:
        reply_message = f"Sorry, I couldn't process your request due to an error: {error}"
        logging.error("Error in sending chatbot reply: %s", error)

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def start(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        welcome_message = "Welcome to the Daily Life Tips Bot. Here you can get tips to improve your day-to-day life."
        subscription_key = f'daily_tip_subscribed_{user_id}'

        # Check whether the user is subscribed or not
        is_subscribed = redis_client.get(subscription_key)

        # Update the button text based on subscription status
        subscribe_button_text = "Unsubscribe from Daily Tips" if is_subscribed else "Subscribe to Daily Tips"

        # Inline keyboard for tip categories
        tip_categories = [
            [InlineKeyboardButton("Health Tips", callback_data='health_tips')],
            [InlineKeyboardButton("Productivity Tips", callback_data='productivity_tips')],
            [InlineKeyboardButton("Relationship Tips", callback_data='relationship_tips')],
            [InlineKeyboardButton("Schedule Timely Tip", callback_data='schedule_timely_tip')],
            [InlineKeyboardButton(subscribe_button_text, callback_data='toggle_subscription')]
        ]
        inline_keyboard = InlineKeyboardMarkup(tip_categories)

        # Reply keyboard for main options
        reply_keyboard_layout = [
            [KeyboardButton("Get a Random Tip")]
        ]
        reply_keyboard = ReplyKeyboardMarkup(reply_keyboard_layout, resize_keyboard=True)

        # Send a message with both the inline and reply keyboards
        update.message.reply_text(welcome_message, reply_markup=reply_keyboard)
        update.message.reply_text("Choose a category or get a random tip:", reply_markup=inline_keyboard)

    except Exception as e:
        logging.error(f"Error in start function: {e}")
        update.message.reply_text("An error occurred while processing your request.")


def schedule_timely_tip(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        # Retrieve the interval from the user's message
        interval_minutes = int(context.args[0])
        job_name = f'timely_tip_{user_id}'
        
        # Remove existing jobs for the user to avoid duplicates
        current_jobs = context.job_queue.get_jobs_by_name(job_name)
        for job in current_jobs:
            job.schedule_removal()

        # Schedule a new job
        context.job_queue.run_repeating(
            send_tip, timedelta(minutes=interval_minutes), 
            context=user_id, name=job_name
        )
        update.message.reply_text(f"You will now receive tips every {interval_minutes} minutes!")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /schedule_timely_tip <minutes>")

def send_tip(context: CallbackContext) -> None:
    user_id = context.job.context
    subscription_key = f'daily_tip_subscribed_{user_id}'

    # Check if the user is subscribed in Redis
    is_subscribed = redis_client.get(subscription_key)

    if is_subscribed:
        message = chatbot_assistant.submit('generate me a prompt to get a wise tip or advice or motivation or lesson or funny. Do not add any extra text or information.')
        tip_message = chatbot_assistant.submit(message)
        context.bot.send_message(chat_id=user_id, text=tip_message)
    else:
        context.job.schedule_removal()
        context.bot.send_message(chat_id=user_id, text='You have unsubscribed from Daily Tips. The scheduled tips have stopped. Subscribe again using /subscription or /start')



def help_command(update: Update, context: CallbackContext) -> None:
    help_message = "Use /start to begin. Get life tips or subscribe to daily updates."
    update.message.reply_text(help_message)

def handle_set_interval(update: Update, context: CallbackContext) -> None:
    if 'awaiting_interval' in context.user_data and context.user_data['awaiting_interval']:
        try:
            interval_minutes = int(update.message.text)
            user_id = update.effective_user.id
            job_name = f'timely_tip_{user_id}'

            # Remove existing jobs for the user to avoid duplicates
            current_jobs = context.job_queue.get_jobs_by_name(job_name)
            for job in current_jobs:
                job.schedule_removal()

            # Schedule a new job
            context.job_queue.run_repeating(
                send_tip, timedelta(minutes=interval_minutes),
                context=user_id, name=job_name
            )
            update.message.reply_text(f"You will now receive tips every {interval_minutes} minutes!")
        except ValueError:
            update.message.reply_text("Invalid input. Please enter a number representing the interval in minutes.")
        finally:
            # Reset the state
            context.user_data['awaiting_interval'] = False
    else:
        # If we are not in the awaiting interval state, handle other text as usual
        send_chatbot_reply(update, context)


def handle_callback_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'health_tips':
        send_category_tip('health', query)
    elif query.data == 'productivity_tips':
        send_category_tip('productivity', query)
    elif query.data == 'relationship_tips':
        send_category_tip('relationships', query)
    elif query.data == 'schedule_timely_tip':
        user_id = update.effective_user.id
        subscription_key = f'daily_tip_subscribed_{user_id}'
        is_subscribed = redis_client.get(subscription_key)
        if is_subscribed:
            context.bot.send_message(chat_id=query.message.chat_id,text="Please enter the interval in minutes for your timely tips (e.g., '5' for every 5 minutes).")
            # Store the state that we're waiting for the user to enter the interval
            context.user_data['awaiting_interval'] = True
        else:
            context.bot.send_message(chat_id=query.message.chat_id,text='Please Subscribe first. /start and then click subscribe.')
    elif query.data == 'toggle_subscription':
        toggle_subscription(query.from_user.id, query,context)
    


def send_category_tip(category: str, query):
    try:
        tip_message = chatbot_assistant.submit(f"Give me a wise life tip about: {category}.")
        query.edit_message_text(text=tip_message)
    except Exception as error:
        query.edit_message_text(text=f"Sorry, there was an issue with your request: {error}")

def toggle_subscription(user_id: int, query,context: CallbackContext):
    subscription_key = f'daily_tip_subscribed_{user_id}'
    if redis_client.get(subscription_key):
        # Delete the subscription key from Redis
        redis_client.delete(subscription_key)
        # Remove existing jobs for the user to stop scheduled tips
        job_name = f'timely_tip_{user_id}'
        current_jobs = context.job_queue.get_jobs_by_name(job_name)
        for job in current_jobs:
            job.schedule_removal()
        query.edit_message_text(text="You have unsubscribed from the Daily Tips. The scheduled tips have stopped.")
    else:
        redis_client.set(subscription_key, 'True')
        query.edit_message_text(text="You're now subscribed to Daily Tips!")

def main():
    updater = Updater(bot_config.TG_ACCESS_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # job_queue = updater.job_queue

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler('subscription',toggle_subscription))
    dispatcher.add_handler(CommandHandler("schedule_timely_tip", schedule_timely_tip, pass_args=True))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_set_interval))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()