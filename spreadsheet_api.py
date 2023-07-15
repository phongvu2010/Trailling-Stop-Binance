import pandas as pd
import streamlit as st
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SpreadSheets:
    def __init__(self, SPREADSHEET_ID):
        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        CLIENT_SECRET_FILE = '.credential/google_api_credentials.json'

        cred_json = '.credential/client_secret.json'

        # The ID a spreadsheet.
        self.SPREADSHEET_ID = SPREADSHEET_ID

        # Shows basic usage of the Sheets API. Prints values from a sample spreadsheet.
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is created
        # automatically when the authorization flow completes for the first time.
        if os.path.exists(CLIENT_SECRET_FILE):
            creds = Credentials.from_authorized_user_file(CLIENT_SECRET_FILE, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_json, SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open(CLIENT_SECRET_FILE, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('sheets', 'v4', credentials = creds)
        except HttpError as err:
            print(err)

    def read_from_gsheet(self, worksheet_name):
        # Call the Sheets API
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId = self.SPREADSHEET_ID,
                                    range = worksheet_name).execute()
        df = pd.DataFrame(result.get('values', []))
        new_header = df.iloc[0].to_list() # grab the first row for the header
        df = df[1:] # take the data less the header row
        df.columns = new_header # set the header row as the df header

        return df.reset_index(drop = True)

    def write_to_gsheet(self, df, worksheet_name):
        try:
            list = [df.columns.to_list()] + df.values.tolist()
            resource = {
                'majorDimension': 'ROWS',
                'values': list
            }

            sheet = self.service.spreadsheets()
            sheet.values().update(
                spreadsheetId = self.SPREADSHEET_ID,
                range = worksheet_name,
                valueInputOption = 'USER_ENTERED',
                body = resource
            ).execute()
        except Exception as e:
            print(e)
