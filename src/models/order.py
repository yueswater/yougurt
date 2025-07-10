from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID

from src.models.constants import TAX_RATE
from src.models.product import Product
from src.utils.format_datetime import format_datetime
from src.utils.format_uuid import format_uuid


class OrderStatus(Enum):
    PENDING = 0
    CONFIRMED = 1
    CANCELLED = -1


class DeliverStatus(Enum):
    PREPARE = 1
    DELIVERING = 2
    DELIVERED = 3


@dataclass
class Order:
    order_id: UUID
    confirmed_order: OrderStatus
    desired_date: datetime
    deliver_date: datetime
    deliver_status: DeliverStatus
    payment_method: str
    member_id: UUID
    orders: Dict[str, int]  # Product: quantity
    order_fee: int
    total_fee: int
    recipient: str
    address: str
    invoice: str
    order_date: datetime = field(default_factory=datetime.now)
    tax: float = TAX_RATE

    @classmethod
    def from_dict(cls, data: Dict) -> "Order":
        return cls(
            order_id=format_uuid(data["order_id"]),
            order_date=format_datetime(data.get("order_date", datetime.now())),
            confirmed_order=OrderStatus[data["confirmed_order"]],
            desired_date=format_datetime(data["desired_date"]),
            deliver_date=format_datetime(data["deliver_date"]),
            deliver_status=DeliverStatus[data["deliver_status"]],
            payment_method=data["payment_method"],
            member_id=format_uuid(data["member_id"]),
            orders=data["orders"],  # dict
            order_fee=data["order_fee"],
            total_fee=data["total_fee"],
            recipient=data["recipient"],
            address=data["address"],
            invoice=data["invoice"],
            tax=data["tax"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_date": self.order_date,
            "confirmed_order": self.confirmed_order.name
            if self.confirmed_order
            else None,
            "desired_date": self.desired_date,
            "deliver_date": (
                self.deliver_date.isoformat()
                if isinstance(self.deliver_date, datetime)
                else str(self.deliver_date)
                if self.deliver_date
                else ""
            ),
            "deliver_status": self.deliver_status.name if self.deliver_status else None,
            "payment_method": self.payment_method,
            "member_id": self.member_id,
            "orders": self.orders,
            "order_fee": self.order_fee,
            "total_fee": self.total_fee,
            "recipient": self.recipient,
            "address": self.address,
            "invoice": self.invoice,
            "tax": self.tax,
        }

    def tax_ratio(self):
        """
        Return the proportion of tax from a tax-included price
        """
        return self.tax / (1 + self.tax)

    def calculate_tax_fee(self, product_map: Dict[str, Product], pid: str) -> float:
        product = product_map.get(pid)
        tax_fee = product.price * self.tax_ratio()
        return tax_fee

    def calculate_fee_detail(self, product_map: Dict[str, Product]) -> Dict[str, float]:
        order_fee = 0
        for pid, qty in self.orders.items():
            product = product_map.get(pid)
            if not product:
                raise ValueError(f"Product ID {pid} not found")
            order_fee += product.price * qty  # price * quantity

        tax_fee = order_fee * self.tax_ratio()
        total_fee = order_fee + tax_fee
        return {"order_fee": order_fee, "tax_fee": tax_fee, "total_fee": total_fee}

    def get_order_items(
        self, product_map: Dict[str, Product]
    ) -> Dict[str, Dict[str, Any]]:
        items = {}
        for pid, qty in self.orders.items():
            product = product_map.get(pid)
            if not product:
                raise ValueError(f"Product ID {pid} not found")
            items[pid] = {
                "name": product.product_name,
                "price": product.price,
                "quantity": qty,
                "subtotal": product.price * qty,
            }
        return items

    @property
    def confirmed_order_text(self) -> str:
        if self.confirmed_order == OrderStatus.CONFIRMED:
            return "已確認"
        elif self.confirmed_order == OrderStatus.PENDING:
            return "待確認"
        elif self.confirmed_order == OrderStatus.CANCELLED:
            return "已取消"
        return "未指定"

    @property
    def deliver_status_text(self) -> str:
        if self.deliver_status == DeliverStatus.PREPARE:
            return "備貨中"
        elif self.deliver_status == DeliverStatus.DELIVERING:
            return "配送中"
        elif self.deliver_status == DeliverStatus.DELIVERED:
            return "已送達"
        return "未指定"

    def __post_init__(self):
        if self.order_fee < 0 or self.total_fee < 0 or self.tax < 0:
            raise ValueError("order_fee, total_fee, and tax cannot be negative")
