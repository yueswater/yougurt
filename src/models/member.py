from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from src.utils.format_datetime import format_datetime
from src.utils.format_uuid import format_uuid


@dataclass
class Member:
    member_id: UUID
    line_id: str
    member_name: str
    create_at: datetime
    phone: str
    order_type: str
    remain_delivery: int
    remain_volume: int
    prepaid: int = 0  # take value only when valid_member = True
    valid_member: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "Member":
        return cls(
            member_id=format_uuid(data["member_id"]),
            line_id=data["line_id"],
            member_name=data["member_name"],
            create_at=format_datetime(data["create_at"]),
            phone=data["phone"],
            order_type=data["order_type"],
            remain_delivery=data["remain_delivery"],
            remain_volume=data["remain_volume"],
            prepaid=data["prepaid"],
            valid_member=data["valid_member"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "member_id": self.member_id,
            "line_id": self.line_id,
            "member_name": self.member_name,
            "create_at": self.create_at,
            "phone": self.phone,
            "order_type": self.order_type,
            "remain_delivery": self.remain_delivery,
            "remain_volume": self.remain_volume,
            "prepaid": self.prepaid,
            "valid_member": self.valid_member,
        }

    def __post_init__(self):
        if self.remain_volume < 0:
            raise ValueError("remain_volume cannot be negative")
        if self.remain_delivery < 0:
            raise ValueError("remain_delivery cannot be negative")
        if self.prepaid < 0:
            raise ValueError("prepaid cannot be negative")
