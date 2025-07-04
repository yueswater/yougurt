from src.repos.member_repo import GoogleSheetMemberRepository

def check_if_user_exists(line_id: str) -> bool:     # Mock version
    repo = GoogleSheetMemberRepository()
    all_users = repo.get_all()
    return any(m for m in all_users if m.line_id == line_id)
