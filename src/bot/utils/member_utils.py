import re
from functools import wraps

from linebot.models import TextSendMessage

from src.repos.member_repo import GoogleSheetMemberRepository


def check_user_exist(func):
    @wraps(func)
    def wrapper(line_id: str, *args, **kwargs):
        repo = GoogleSheetMemberRepository()
        all_users = repo.get_all()
        if any(m for m in all_users if m.line_id == line_id):
            return TextSendMessage("⚠️ 您的帳號已完成綁定，請勿重複註冊。")
        return func(line_id, *args, **kwargs)

    return wrapper


def validate_phone_format(func):
    @wraps(func)
    def wrapper(line_id: str, phone: str, *args, **kwargs):
        pattern = r"^09\d{8}$|^09\d{2}-\d{6}$|^09\d{2}-\d{3}-\d{3}$"
        if not re.fullmatch(pattern, phone):
            return TextSendMessage(text="手機號碼格式錯誤，請重新輸入，例如：0912345678 或 0912-345678")
        return func(line_id, phone, *args, **kwargs)

    return wrapper
