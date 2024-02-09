from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Hello from Big At Heart !\nSign up with /register"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')

start_handler = CommandHandler('start', start)