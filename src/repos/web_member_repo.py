from typing import Optional

from src.utils.password_utils import check_password
from src.utils.sheet_client import get_worksheet


class GoogleSheetWebMemberRepository:
    def __init__(self):
        self.worksheet = get_worksheet("Web Member")

    def add_user(self, username: str, password: str, fullname: str) -> None:
        row = ["", username, password, fullname]
        self.worksheet.append_row(row)

    def exists(self, username: str) -> bool:
        all_rows = self.worksheet.get_all_records()
        return any(r["Username"] == username for r in all_rows)

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        users = self.worksheet.get_all_records()
        for user in users:
            if user["Username"] == username and check_password(
                password, user["Password"]
            ):
                return user
        return None
