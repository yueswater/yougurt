import os

import gspread
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


def get_worksheet(sheet_name: str):
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
    sh = gc.open_by_key(SHEET_ID)
    return sh.worksheet(sheet_name)
