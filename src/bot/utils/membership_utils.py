from src.repos.member_repo import GoogleSheetMemberRepository
from functools import wraps

def check_user_exist(func):
    @wraps(func)
    def wrapper(line_id: str, *args, **kwargs):
        repo = GoogleSheetMemberRepository()
        all_users = repo.get_all()
        if not any(m for m in all_users if m.line_id == line_id):
            raise ValueError("user not found")
        return func(line_id, *args, **kwargs)
    return wrapper
