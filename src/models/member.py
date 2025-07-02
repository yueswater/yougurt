from uuid import UUID, uuid4
from dataclasses import dataclass
from typing import Dict

@dataclass
class Member:
    member_id: UUID
    line_id: str
    member_name: str
    order_type: str
    remain_delivery: int
    prepaid: int

    @classmethod
    def from_file(cls, data: Dict):
        uid = data["member_id"]
        if not isinstance(uid, UUID):
            uid = UUID(uid)
        return cls(
            member_id=uid,
            line_id=data["line_id"],
            member_name=data["member_name"],
            order_type=data["order_type"],
            remain_delivery=data["remain_delivery"],
            prepaid=data["prepaid"]
        )