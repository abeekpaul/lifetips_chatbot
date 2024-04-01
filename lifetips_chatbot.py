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
from ChatGPT import HKBU_ChatGPT
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackQueryHandler
import aws_params



def equiped_chatgpt(update: Update, context: CallbackContext) -> None:
    global chatgpt
    personalizedPrompt = "Discussing movies and TVshows : "
    prompt = personalizedPrompt + update.message.text
    reply_message = hkbu_chatgpt.submit(prompt)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Instantiate HKBU_ChatGPT
hkbu_chatgpt = HKBU_ChatGPT()

r=redis.Redis(host=aws_params.REDIS_HOST, port=int(aws_params.REDIS_PORT), password=aws_params.REDIS_PASSWORD)

# Initial Logging Configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 用于创建返回和主菜单按钮的函数
def back_to_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Return to Start", callback_data='start')],
        [InlineKeyboardButton("Help", callback_data='help')]
    ])

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = "Welcome to the Netflix Recommendation Bot. Here you can get recommendations based on Category or Mood, and view your history."

    buttons = [
        [InlineKeyboardButton("Category", callback_data='category')],
        [InlineKeyboardButton("Mode", callback_data='mode')],
        [InlineKeyboardButton("History", callback_data='history')]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose:', reply_markup=keyboard)

def help_command(update: Update, context: CallbackContext) -> None:
    help_text = "Use /start to start. Choose Your Preferences for Netflix Recommendations."
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == 'category':
        buttons = [
            [InlineKeyboardButton("Sci-Fi", callback_data='category_scifi')],
            [InlineKeyboardButton("Comedy", callback_data='category_comedy')]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        query.edit_message_text(text="Choose Category:", reply_markup=keyboard)
    elif query.data.startswith('category_'):
        category = query.data.split('_')[1]
        # Use HKBU GPT to get recommendation
        try:
            recommendation = hkbu_chatgpt.submit(f"Find some popular {category} content on Netflix.")
            query.edit_message_text(text=recommendation)
            # Update history
            update_history(user_id, recommendation)
        except Exception as e:
            query.edit_message_text(text=f"Sorry, there was an issue with your request: {e}")
    elif query.data == 'mode':
        buttons = [
            [InlineKeyboardButton("Cozy", callback_data='mode_cozy')],
            [InlineKeyboardButton("Excited", callback_data='mode_excited')]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        query.edit_message_text(text="Choose mode:", reply_markup=keyboard)
    elif query.data.startswith('mode_'):
        mode = query.data.split('_')[1]
        try:
            recommendation = hkbu_chatgpt.submit(f"Find something popular on Netflix that fits the {mode} mood!")
            query.edit_message_text(text=recommendation)
            # Update history
            update_history(user_id, recommendation)
        except Exception as e:
            query.edit_message_text(text=f"Sorry, there was an issue with your request: {e}")
    elif query.data == 'history':
        history = get_history(user_id)
        query.edit_message_text(text="Your History recommendation:\n" + history)

def update_history(user_id, message):
    # 以 user_id 为 key 存储用户的推荐历史
    r.lpush(user_id, message)
    r.ltrim(user_id, 0, 4)  # 只保留最近的5条记录

def get_history(user_id):
    # Fetch the entire history
    full_history = [f"{idx + 1}. {item.decode('utf-8')}" for idx, item in enumerate(r.lrange(user_id, 0, -1))]
    # Get the last part of the history (e.g., last 5 items)
    last_part_history = full_history[-5:]
    return '\n'.join(last_part_history)


def main():
    token = aws_params.TG_ACCESS_TOKEN

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
