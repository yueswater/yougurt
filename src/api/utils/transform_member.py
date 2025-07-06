from src.api.schemas.member_schema import MemberIn
from src.models.member import Member


def to_domain_member(member_in: MemberIn) -> Member:
    return Member.from_dict(member_in.model_dump())
