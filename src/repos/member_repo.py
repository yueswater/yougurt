from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID

from src.models.member import Member
from src.utils.sheet_client import get_worksheet


class MemberRepository(ABC):
    @abstractmethod
    def add(self, member: Member) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Member]:
        pass

    @abstractmethod
    def get_by_member_id(self, member_id: UUID) -> Optional[Member]:
        pass


class GoogleSheetMemberRepository(MemberRepository):
    def __init__(self):
        super().__init__()
        self.worksheet = get_worksheet("Members")

    def add(self, member: Member) -> None:
        data = member.to_dict()
        row = [
            str(data["member_id"]),
            data["line_id"],
            data["member_name"],
            data["create_at"].isoformat(),
            data["order_type"],
            data["remain_delivery"],
            data["prepaid"],
        ]
        self.worksheet.append_row(row)

    def get_all(self) -> List[Member]:
        rows = self.worksheet.get_all_records()
        members = []
        for row in rows:
            data = {
                "member_id": row["Member ID"],
                "line_id": row["Line ID"],
                "member_name": row["Member Name"],
                "create_at": row["Create at"],
                "order_type": row["Order Type"],
                "remain_delivery": row["Remain Delivery"],
                "prepaid": row["Prepaid"],
            }
            members.append(Member.from_dict(data))
        return members

    def get_by_member_id(self, member_id: Union[str, UUID]) -> Optional[Member]:
        all_members = self.get_all()
        if not isinstance(member_id, UUID):
            member_id = UUID(member_id)

        member = next((m for m in all_members if m.member_id == member_id), None)
        return member.to_dict() if member else None
