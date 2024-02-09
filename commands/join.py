from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
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

ACTIVITY_ID, ENROLL_CONFIRMATION = range(2)

###### HELPER FUNCTIONS ######

def check_user_enrolled(user_id):
    # Check if user is enrolled and approval status is true
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Volunteer Details!A:F").execute()
    values = result.get("values", [])
    for row in values:
        if str(user_id) == row[0] and row[5].lower() == 'true':
            return True
    return False

def check_activity_id(activity_id):
    # Check if activity ID exists
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    activity_ids = [sheet['properties']['title'] for sheet in result['sheets']]
    return activity_id in activity_ids

def check_user_already_enrolled(user_id, activity_id):
    # Check if user has already enrolled in the activity
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{activity_id}!A:A").execute()
        values = result.get("values", [])
        user_ids = [value[0] for value in values if value]
        return str(user_id) in user_ids
    except HttpError as e:
        print(f"An error occurred: {e}")
        return False

def check_user_already_joined(user_id, activity_id):
    # Check if user has already joined the activity
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{activity_id}!A:F").execute()
    values = result.get("values", [])
    for row in values:
        if str(user_id) == row[0]:
            return True
    return False

## LOGIC 

async def start_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To join an activity, please enter the activity ID.")
    return ACTIVITY_ID

async def get_activity_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activity_id = update.message.text.strip().upper()

    # Check if user is enrolled and approval status is true
    if not check_user_enrolled(update.effective_user.id):
        await update.message.reply_text("You need to enroll first before joining an activity. Do /enroll to check your enrollment status.")
        return ConversationHandler.END

    # Check if activity ID exists
    if not check_activity_id(activity_id):
        await update.message.reply_text("Invalid activity ID. Please try again.")
        return ACTIVITY_ID

    # Check if user has already enrolled in the activity
    if check_user_already_enrolled(update.effective_user.id, activity_id):
        await update.message.reply_text("You are already enrolled in this activity.")
        return ConversationHandler.END

    # Check if user has already joined the activity
    if check_user_already_joined(update.effective_user.id, activity_id):
        await update.message.reply_text("You have already joined this activity.")
        return ConversationHandler.END

    context.user_data['activity_id'] = activity_id
    await update.message.reply_text(f"You are about to join activity {activity_id}. "
                              f"Please confirm by typing 'yes'.")
    return ENROLL_CONFIRMATION

async def confirm_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text.strip().lower()
    if confirmation == 'yes':
        # Add user details to activity sheet
        add_user_to_activity_sheet(update.effective_user.id, context.user_data['activity_id'])

        await update.message.reply_text("You have successfully joined the activity!")
    else:
        await update.message.reply_text("Enrollment canceled.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_enrollment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enrollment canceled.")
    context.user_data.clear()
    return ConversationHandler.END

def add_user_to_activity_sheet(user_id, activity_id):
    # Add user details to activity sheet
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    user_details = get_user_details(user_id)
    # Default False for attendance
    user_details.append(False)
    if user_details:
        values = [user_details]
        body = {'values': values}

        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{activity_id}!A1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        print(f"{result.get('updates').get('updatedCells')} cells appended to {activity_id} sheet.")
    else:
        print("User details not found.")

def get_user_details(user_id):
    # Get user details from Volunteer Details sheet
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Volunteer Details!A:F").execute()
    values = result.get("values", [])
    for row in values:
        if str(user_id) == row[0]:
            return row[0:5]
    return None

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

join_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('join', start_join)],
    states={
        ACTIVITY_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_activity_id)],
        ENROLL_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_enrollment)],
    },
    fallbacks=[CommandHandler('cancel', cancel_enrollment)],
    allow_reentry=True
)
