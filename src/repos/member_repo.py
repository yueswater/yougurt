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
    def update(self, member: Member) -> None:
        pass

    @abstractmethod
    def delete(self, line_id: str) -> None:
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
            data["phone"],
            data["order_type"],
            data["remain_delivery"],
            data["remain_volume"],
            data["prepaid"],
            data["valid_member"],
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
                "phone": row["Phone"],
                "order_type": row["Order Type"],
                "remain_delivery": row["Remain Delivery"],
                "remain_volume": row["Remain Volume"],
                "prepaid": row["Prepaid"],
                "valid_member": row["Valid Member"],
            }
            members.append(Member.from_dict(data))
        return members

    def get_by_member_id(self, member_id: Union[str, UUID]) -> Optional[Member]:
        return next((m for m in self.get_all() if m.member_id == member_id), None)

    def get_by_line_id(self, line_id: str) -> Optional[Member]:
        return next((m for m in self.get_all() if m.line_id == line_id), None)

    def exists(self, line_id: str) -> bool:
        return any(m.line_id == line_id for m in self.get_all())

    def is_valid_member(self, line_id: str) -> bool:
        member = self.get_by_line_id(line_id)
        return member.valid_member if member else False

    def update(self, member: Member) -> None:
        all_rows = self.worksheet.get_all_records()

        target_row_idx = next(
            (i for i, row in enumerate(all_rows) if row["Line ID"] == member.line_id),
            None,
        )

        if target_row_idx is None:
            raise ValueError(f"找不到 line_id={member.line_id} 的會員")

        target_row_idx + 2

        data = member.to_dict()
        new_row = [
            str(data["member_id"]),
            data["line_id"],
            data["member_name"],
            data["create_at"].isoformat(),
            data["phone"],
            data["order_type"],
            data["remain_delivery"],
            data["remain_volume"],
            data["prepaid"],
            data["valid_member"],
        ]

        # Overwrite data
        self.worksheet.update(values=[new_row], range_name="A2:J2")

    def delete(self, line_id: str) -> None:
        member = self.get_by_line_id(line_id)
        if not member:
            raise ValueError(f"找不到 line_id={member.line_id} 的會員")

        member.valid_member = False
        self.update(member)
