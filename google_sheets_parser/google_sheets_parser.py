from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import re


class GSheetsParser:
    def __init__(self, sheet_link):
        self.sheet_id = self.__extract_sheet_id(sheet_link)
        self.__scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.__creds = self.__get_creds()
        try:
            self.__service = build('sheets', 'v4', credentials=self.__creds)
        except HttpError as err:
            print(err)

    def validate_user_table_link(self):
        columns = self.parse(sheet_range='A1:F1')
        return columns == [['platform', 'campaign_id', 'campaign_name', 'date', 'impressions', 'clicks']]

    def parse(self, sheet_range='A:F'):
        try:
            sheet = self.__service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.sheet_id, range=sheet_range).execute()
            values = result.get('values', [])
            return values
        except HttpError as err:
            print(err)
            return []

    @staticmethod
    def __extract_sheet_id(link):
        match = re.search(r"/d/(.*?)/", link)
        if match:
            return match.group(1)
        else:
            return None

    def __get_creds(self):
        creds = None
        if os.path.exists('../tokens/token.json'):
            creds = Credentials.from_authorized_user_file('../tokens/token.json', self.__scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../tokens/credentials.json', self.__scopes)
                creds = flow.run_local_server(port=0)
            with open('../tokens/token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
