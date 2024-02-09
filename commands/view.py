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

async def view_activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get user ID
    user_id = update.effective_user.id
    
    # Fetch user's joined activities
    joined_activities = get_joined_activities(user_id)

    if not joined_activities:
        await update.message.reply_text("You haven't joined any activities yet.")
        return

    message = "*Joined Activities:*\n"
    for activity in joined_activities:
        message += f"- {activity}\n"

    await update.message.reply_markdown(message)


def get_joined_activities(user_id):
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    events_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Events!A2:F100").execute()
    activity_ids = [activity[1] for activity in events_data['values']]
    joined_activities = []

    for activity_id in activity_ids:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{activity_id}!A2:F100").execute()
        volunteer_ids = [row[0] for row in result.get('values', [])]

        if str(user_id) in volunteer_ids:
            joined_activities.append(activity_id)

    return joined_activities

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

view_activities_handler = CommandHandler('view', view_activities)
