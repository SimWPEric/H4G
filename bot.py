import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from config import telegram_token
from commands import register, start, activities, join, view, certificate

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    
    start_handler = CommandHandler('start', start.start)
    application.add_handler(start_handler)

    application.add_handler(register.register_conversation_handler)

    activities_handler = CommandHandler('activities', activities.activities)
    application.add_handler(activities_handler)

    application.add_handler(join.join_conversation_handler)

    application.add_handler(view.view_activities_handler)
    
    application.add_handler(certificate.certificate_conv_handler)

    application.run_polling()