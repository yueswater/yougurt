from abc import ABC, abstractmethod
from typing import List, Optional
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
        raise NotImplementedError("get_all() not implemented yet")

    def get_by_member_id(self, member_id: UUID) -> Optional[Member]:
        raise NotImplementedError("get_by_member_id() not implemented yet")
