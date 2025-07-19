import json
import os

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# global cache
_gc = None
_spreadsheet = None


def get_worksheet(sheet_name: str, force_reload: bool = False):
    global _gc, _spreadsheet

    if force_reload or _gc is None or _spreadsheet is None:
        if not SERVICE_ACCOUNT_JSON:
            raise RuntimeError("Missing SERVICE_ACCOUNT_JSON env variable")

        info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        _gc = gspread.authorize(creds)
        _spreadsheet = _gc.open_by_key(SHEET_ID)

    return _spreadsheet.worksheet(sheet_name)
