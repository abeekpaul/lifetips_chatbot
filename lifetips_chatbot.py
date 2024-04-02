from asyncore import dispatcher_with_send
import os
import logging
from httpx import QueryParams
import redis
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext.filters import MessageFilter
import logging
from telegram.ext import MessageHandler
from telegram.ext import Filters
from chatbot import ChatbotAssistant
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import bot_config

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Redis connection
redis_client = redis.Redis(host=bot_config.REDIS_HOST, port=int(bot_config.REDIS_PORT), password=bot_config.REDIS_PASSWORD)

# Initialize Chatbot Assistant
chatbot_assistant = ChatbotAssistant()

def send_chatbot_reply(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    life_tips_prompt = f"Providing life tips: {user_message}"
    try:
        reply_message = chatbot_assistant.submit_query(life_tips_prompt)
    except Exception as error:
        reply_message = f"Sorry, I couldn't process your request due to an error: {error}"
        logging.error("Error in sending chatbot reply: %s", error)

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def start(update: Update, context: CallbackContext) -> None:
    welcome_message = "Welcome to the Daily Life Tips Bot. Here you can get tips to improve your day-to-day life."

    tip_categories = [
        InlineKeyboardButton("Health Tips", callback_data='health_tips'),
        InlineKeyboardButton("Productivity Tips", callback_data='productivity_tips'),
        InlineKeyboardButton("Relationship Tips", callback_data='relationship_tips'),
        InlineKeyboardButton("Subscribe to Daily Tips", callback_data='subscribe_daily_tips')
    ]
    keyboard_layout = [[button] for button in tip_categories]
    keyboard = InlineKeyboardMarkup(keyboard_layout)

    update.message.reply_text(welcome_message, reply_markup=keyboard)

def help_command(update: Update, context: CallbackContext) -> None:
    help_message = "Use /start to begin. Get life tips or subscribe to daily updates."
    update.message.reply_text(help_message)

def handle_callback_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'health_tips':
        send_category_tip('health', query)
    elif query.data == 'productivity_tips':
        send_category_tip('productivity', query)
    elif query.data == 'relationship_tips':
        send_category_tip('relationships', query)
    elif query.data == 'subscribe_daily_tips':
        toggle_subscription(query.from_user.id, query)

def send_category_tip(category: str, query):
    try:
        tip_message = chatbot_assistant.submit_query(f"Give me a life tip about {category}.")
        query.edit_message_text(text=tip_message)
    except Exception as error:
        query.edit_message_text(text=f"Sorry, there was an issue with your request: {error}")

def toggle_subscription(user_id: int, query):
    subscription_key = f'daily_tip_subscribed_{user_id}'
    if redis_client.get(subscription_key):
        redis_client.delete(subscription_key)
        query.edit_message_text(text="You have unsubscribed from the Daily Tips.")
    else:
        redis_client.set(subscription_key, 'true')
        query.edit_message_text(text="You're now subscribed to Daily Tips!")

def main():
    updater = Updater(bot_config.TG_ACCESS_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), send_chatbot_reply))

    # Set up the Background Scheduler for daily tips
    scheduler = BackgroundScheduler()
    # Assume schedule_daily_tips function is defined elsewhere to schedule the tips
    # schedule_daily_tips(scheduler)
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
