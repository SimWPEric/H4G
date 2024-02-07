from telegram import Update
from telegram.ext import ContextTypes

import os 
from config import DB_ID

from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError 

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = DB_ID

def view_activities(): 
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


    try: 
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets() 

        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Events!A2:D3").execute()

        values = result.get("values", [])
        return values
    except HttpError as error:
        print(error)


async def activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activities = view_activities()
    
    message = "<b>Activities:</b>\n\n"
    
    for activity in activities:
        activity_text = f"<b>{activity[0]}</b>\n<b>ID:</b> {activity[1]}\n<b>Description:</b>{activity[2]}\n<b>Link:</b>{activity[3]}\n\n"
        message += activity_text
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML')
