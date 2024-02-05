from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from telegram import Update

NAME, EMAIL, PHONE, AGE = range(4)

async def start_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the enrollment process! Please provide your name.")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Thank you, {context.user_data['name']}! Please provide your email address.")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Great! Now, please provide your phone number.")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Got it! Finally, please provide your age.")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    enrollment_details = (
        f"Enrollment completed!\n"
        f"Name: {context.user_data['name']}\n"
        f"Email: {context.user_data['email']}\n"
        f"Phone: {context.user_data['phone']}\n"
        f"Age: {context.user_data['age']}"
    )
    await update.message.reply_text(enrollment_details)

    context.user_data.clear()

    return ConversationHandler.END

async def cancel_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enrollment process canceled.")
    context.user_data.clear()

    return ConversationHandler.END

enroll_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('enroll', start_enrollment)],
    states={
        NAME: [MessageHandler(filters.TEXT, get_name)],
        EMAIL: [MessageHandler(filters.TEXT, get_email)],
        PHONE: [MessageHandler(filters.TEXT, get_phone)],
        AGE: [MessageHandler(filters.TEXT, get_age)],
    },
    fallbacks=[CommandHandler('cancel', cancel_enrollment)],
    allow_reentry=True
)
