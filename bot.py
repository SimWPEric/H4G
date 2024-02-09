import logging
from telegram.ext import ApplicationBuilder
from config import telegram_token
from commands import start, help, register, activities, join, view, certificate

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_token).build()
    
    application.add_handler(start.start_handler)
    application.add_handler(help.help_handler)
    application.add_handler(register.register_conversation_handler)
    application.add_handler(activities.activities_handler)
    application.add_handler(join.join_conversation_handler)
    application.add_handler(view.view_activities_handler)
    application.add_handler(certificate.certificate_conv_handler)

    application.run_polling()