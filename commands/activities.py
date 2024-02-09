from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

        # Check if the sheet named after activity ID exists, if not, create it
        activity_ids = set()
        result = sheets.get(spreadsheetId=SPREADSHEET_ID).execute()
        for sheet in result['sheets']:
            activity_ids.add(sheet['properties']['title'])

        # Fetch data from existing sheet 'Events'
        result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="Events!A:D").execute()

        # Extract values
        values = result.get("values", [])
        values = values[1::]

        # Create sheets for activities if they don't exist
        for activity in values:
            activity_id = activity[1]
            if activity_id not in activity_ids:
                body = {
                    'requests': [
                        {
                            'addSheet': {
                                'properties': {
                                    'title': activity_id
                                }
                            }
                        }
                    ]
                }

                # Execute the request to create a new sheet
                sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

                # Populate the newly created sheet with headers
                header_values = [['User ID', 'Name', 'Email', 'Phone Number', 'Age', 'Attendance']]
                sheets.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{activity_id}!A1:F1",
                    valueInputOption='RAW',
                    body={'values': header_values}
                ).execute()

                activity_ids.add(activity_id)

        return values

    except HttpError as error:
        print(error)




async def activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activities = view_activities()
    
    message = "<b>Activities:</b>\n\n"
    
    for activity in activities:
        activity_text = f"<b>{activity[0]}</b>\n<b>ID:</b> {activity[1]}\n<b>Description:</b>{activity[2]}\n<b>Link:</b>{activity[3]}\n\n"
        message += activity_text

    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='HTML', reply_markup=reply_markup)
