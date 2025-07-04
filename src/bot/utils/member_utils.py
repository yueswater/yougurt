from src.repos.member_repo import GoogleSheetMemberRepository
from functools import wraps
from linebot.models import TextSendMessage

def check_user_exist(func):
    @wraps(func)
    def wrapper(line_id: str, *args, **kwargs):
        repo = GoogleSheetMemberRepository()
        all_users = repo.get_all()
        if any(m for m in all_users if m.line_id == line_id):
            return TextSendMessage("⚠️ 您的帳號已完成綁定，請勿重複註冊。")
        return func(line_id, *args, **kwargs)
    return wrapper
