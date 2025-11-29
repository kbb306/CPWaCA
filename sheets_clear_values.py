from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import authorize
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of the spreadsheet to clear.
SPREADSHEET_ID = 'your_spreadsheet_id'
RANGE_NAME = 'Sheet1!A1:Z' # Or a specific range like 'Sheet1!A1:D10'

def clear_sheet(spreadsheetId,range):
    creds = authorize.authcheck()
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # ... (code to load/create credentials, similar to Sheets API quickstart)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API to clear the values.
    body = {}
    result = service.spreadsheets().values().clear(
        spreadsheetId, range, body=body).execute()

    print(f"{result.get('clearedRange')} cleared.")

