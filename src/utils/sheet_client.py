import base64
import os

import gspread
from dotenv import load_dotenv

load_dotenv()

# === 憑證處理 ===
SERVICE_ACCOUNT_PATH = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_JSON_PATH", "credentials/yougurt.json"
)
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# 若有 GOOGLE_CREDS_BASE64 且憑證檔案不存在，就寫入
if os.getenv("GOOGLE_CREDS_BASE64") and not os.path.exists(SERVICE_ACCOUNT_PATH):
    os.makedirs(os.path.dirname(SERVICE_ACCOUNT_PATH), exist_ok=True)
    with open(SERVICE_ACCOUNT_PATH, "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDS_BASE64"]))

# === gspread 全域快取 ===
_gc = None
_spreadsheet = None


def get_worksheet(sheet_name: str, force_reload: bool = False):
    global _gc, _spreadsheet

    if force_reload or _gc is None or _spreadsheet is None:
        _gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
        _spreadsheet = _gc.open_by_key(SHEET_ID)

    return _spreadsheet.worksheet(sheet_name)
