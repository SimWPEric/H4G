from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from telegram import Update
import os
from config import DB_ID

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = DB_ID

NAME, EMAIL, PHONE, AGE = range(4)

async def start_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user_id already exists in Google Sheets
    if check_user_id_exists(user_id):
        # Check if user's enrollment is approved
        if not check_approval_status(user_id):
            await update.message.reply_text("Your application is being processed.")
            return ConversationHandler.END
        else:
            await update.message.reply_text("You have already enrolled.")
            return ConversationHandler.END
    
    context.user_data['user_id'] = user_id
    await update.message.reply_text("Welcome to the enrollment process! Please provide your name.")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Please provide a valid name (at least 2 characters).")
        return NAME
    context.user_data['name'] = name
    await update.message.reply_text(f"Thank you, {name}! Please provide your email address.")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not email or not email.count('@') == 1 or not email.count('.') >= 1:
        await update.message.reply_text("Please provide a valid email address.")
        return EMAIL
    context.user_data['email'] = email
    await update.message.reply_text("Great! Now, please provide your phone number.")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not phone.isdigit() or len(phone) != 8:
        await update.message.reply_text("Please provide a valid phone number.")
        return PHONE
    context.user_data['phone'] = phone
    await update.message.reply_text("Got it! Finally, please provide your age.")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text.strip()
    if not age.isdigit():
        await update.message.reply_text("Please provide a valid age.")
        return AGE
    context.user_data['age'] = age
    enrollment_details = (
        f"Enrollment completed! Please wait for your enrollment to be approved. \n"
        f"Name: {context.user_data['name']}\n"
        f"Email: {context.user_data['email']}\n"
        f"Phone: {context.user_data['phone']}\n"
        f"Age: {age}"
    )
    await update.message.reply_text(enrollment_details)

    # Write data to Google Sheets
    write_to_spreadsheet(context.user_data)

    context.user_data.clear()

    return ConversationHandler.END

async def cancel_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enrollment process canceled.")
    context.user_data.clear()

    return ConversationHandler.END

def check_user_id_exists(user_id):
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Volunteer Details!A:A").execute()
    values = result.get("values", [])
    user_ids = [value[0] for value in values]
    
    return str(user_id) in user_ids

def check_approval_status(user_id):
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Volunteer Details!A:F").execute()
    values = result.get("values", [])
    for row in values:
        if str(user_id) == row[0] and row[5].lower() == 'false':
            return False
    return True

def write_to_spreadsheet(data):
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    values = [
        [data['user_id'], data['name'], data['email'], data['phone'], data['age'], False]  # default False for Approval Status
    ]
    body = {
        'values': values
    }

    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Volunteer Details!A1",
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")


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
