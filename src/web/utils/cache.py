from functools import lru_cache

from src.repos.member_repo import GoogleSheetMemberRepository


@lru_cache(maxsize=1)
def get_cached_members():
    return GoogleSheetMemberRepository().get_all()
