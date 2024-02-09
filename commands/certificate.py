from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from config import DB_ID
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = DB_ID
USER_ID_INDEX = 0
ACTIVITY_ID_INDEX = 1
ATTENDANCE_INDEX = 2
CERTIFICATE_STATUS_INDEX = 3

GET_ACTIVITY_ID = 0

def get_credentials():
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
    return credentials

async def start_certificate(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter the activity ID:")
    return GET_ACTIVITY_ID

async def get_activity_id(update: Update, context: CallbackContext):
    activity_id = update.message.text
    user_id = update.effective_user.id

    # Check if the activity ID exists
    if not activity_exists(activity_id):
        await update.message.reply_text("The activity ID you provided does not exist.")
        return ConversationHandler.END

    # Check if the user is enrolled in the activity and has attendance marked
    if user_attended_activity(user_id, activity_id):
        # Check if the certificate request already exists
        if not certificate_request_exists(user_id, activity_id):
            # Append the certificate request to the Google Sheets document
            append_certificate_request(user_id, activity_id)
            await update.message.reply_text("Certificate request sent!")
        else:
            await update.message.reply_text("You have already requested a certificate for this activity.")
    else:
        await update.message.reply_text("You are not enrolled in this activity or attendance not marked.")

    return ConversationHandler.END

def user_attended_activity(user_id, activity_id):
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    # Get data from the activity sheet
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{activity_id}!A:F"  
    ).execute()
    values = result.get("values", [])

    # Check if user_id exists in the activity sheet
    for row in values:
        if str(user_id) in row:
            return True

    return False

def certificate_request_exists(user_id, activity_id):
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Certificates!A2:F100"
    ).execute()
    values = result.get("values", [])

    for row in values:
        if row[USER_ID_INDEX] == str(user_id) and row[ACTIVITY_ID_INDEX] == activity_id:
            return True

    return False

def append_certificate_request(user_id, activity_id):
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    values = [[str(user_id), activity_id, "false"]]
    body = {
        "values": values
    }

    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Certificates!A2:F100",
        valueInputOption="RAW",
        body=body
    ).execute()

def activity_exists(activity_id):
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{activity_id}!A1:F1"  # Assuming data range is from column A to F, adjust as needed
        ).execute()
        return bool(result.get("values", []))
    except:
        return False

# Define conversation handler with two states
certificate_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('certificate', start_certificate)],
    states={
        GET_ACTIVITY_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_activity_id)],
    },
    fallbacks=[]
)
