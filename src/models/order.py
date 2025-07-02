from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from src.utils.format_datetime import format_datetime
from src.utils.format_uuid import format_uuid


@dataclass
class Order:
    order_id: UUID
    order_date: datetime
    shipping_date: datetime
    shipping_status: str
    payment_method: str
    member_id: UUID
    orders: Dict[str, int]  # Product: quantity
    order_fee: int
    total_fee: int
    address: str
    invoice: str
    tax: int

    def __post_init__(self):
        if self.order_fee < 0 or self.total_fee < 0 or self.tax < 0:
            raise ValueError("order_fee, total_fee, and tax cannot be negative")

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            order_id=format_uuid(data["order_id"]),
            order_date=format_datetime(data["order_date"]),
            shipping_date=format_datetime(data["shipping_date"]),
            shipping_status=data["shipping_status"],
            payment_method=data["payment_method"],
            member_id=format_uuid(data["member_id"]),
            orders=data["orders"],
            order_fee=data["order_fee"],
            total_fee=data["total_fee"],
            address=data["address"],
            invoice=data["invoice"],
            tax=data["tax"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_date": self.order_date,
            "shipping_date": self.shipping_date,
            "shipping_status": self.shipping_status,
            "payment_method": self.payment_method,
            "member_id": self.member_id,
            "orders": self.orders,
            "order_fee": self.order_fee,
            "total_fee": self.total_fee,
            "address": self.address,
            "invoice": self.invoice,
            "tax": self.tax,
        }
