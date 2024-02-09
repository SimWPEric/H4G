from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
<b>Commands:</b>
/register : Sign up
/activities : Available activities
/join : Participate in a volunteer activity
/view : Activities joined
/certificate : Request for your certificate 
"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')

help_handler = CommandHandler('help', help)