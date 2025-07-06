from src.repos.member_repo import GoogleSheetMemberRepository, MemberRepository


def get_member_repo() -> MemberRepository:
    return GoogleSheetMemberRepository()
