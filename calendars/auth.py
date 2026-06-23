import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from common.config import TOKEN_PATH, CREDENTIALS_PATH

SCOPES = [
        "https://www.googleapis.com/auth/calendar",
    ]

def calendar_api(google_api_path: str=TOKEN_PATH):
    # If modifying these scopes, delete the file token.json
    creds = None

    if os.path.exists(google_api_path):
        creds = Credentials.from_authorized_user_file(google_api_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(
                host="127.0.0.1",
                port=8080,
                open_browser=False
            )
            # Save the credentials for the next run
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

    try:
        calendar_service = build("calendar", "v3", credentials=creds)
    except HttpError as e:
        print(f"An error occurred: {e}")
    
    return calendar_service