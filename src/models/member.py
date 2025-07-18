from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID

from src.utils.format_datetime import format_datetime
from src.utils.format_uuid import format_uuid


class PaymentStatus(Enum):
    UNPAID = 0
    PAID = 1


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
    remain_free_quota: int
    payment_status: PaymentStatus
    balance: int = 0
    valid_member: bool = False
    bank_account: str = ""

    @classmethod
    def from_dict(cls, data: Dict) -> "Member":
        raw_status = data["payment_status"]
        payment_status = (
            PaymentStatus[raw_status]
            if isinstance(raw_status, str)
            else PaymentStatus(raw_status)
        )
        return cls(
            member_id=format_uuid(data["member_id"]),
            line_id=data["line_id"],
            member_name=data["member_name"],
            create_at=format_datetime(data["create_at"]),
            phone=str(data["phone"]),
            order_type=data["order_type"],
            remain_delivery=data["remain_delivery"],
            remain_volume=data["remain_volume"],
            payment_status=payment_status,
            balance=data["balance"],
            valid_member=data["valid_member"],
            bank_account=data["bank_account"],
            remain_free_quota=data["remain_free_quota"],
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
            "payment_status": self.payment_status.name if self.payment_status else None,
            "balance": self.balance,
            "valid_member": self.valid_member,
            "bank_account": self.bank_account,
            "remain_free_quota": self.remain_free_quota,
        }
