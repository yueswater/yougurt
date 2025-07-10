import os

import gspread
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# global cache
_gc = None
_spreadsheet = None


def get_worksheet(sheet_name: str, force_reload: bool = False):
    global _gc, _spreadsheet

    if force_reload or _gc is None or _spreadsheet is None:
        _gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
        _spreadsheet = _gc.open_by_key(SHEET_ID)

    return _spreadsheet.worksheet(sheet_name)
