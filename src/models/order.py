from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID

from src.models.constants import TAX_RATE
from src.models.product import Product
from src.utils.format_datetime import format_datetime
from src.utils.format_uuid import format_uuid
from src.utils.safe_float import safe_float
from src.utils.safe_int import safe_int


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
    tax: float
    total_fee: int
    delivery_fee: int
    recipient: str
    address: str
    invoice: int
    order_date: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: Dict) -> "Order":
        # Anti-duty treatment OrderStatus
        confirmed_str = data.get("confirmed_order", "").strip()
        try:
            confirmed_order = OrderStatus[confirmed_str]
        except KeyError:
            confirmed_order = OrderStatus.PENDING

        # Anti-duty treatment DeliverStatus
        deliver_str = data.get("deliver_status", "").strip()
        try:
            deliver_status = DeliverStatus[deliver_str]
        except KeyError:
            deliver_status = None  # or DeliverStatus.PREPARE, if you have a preset
        return cls(
            order_id=format_uuid(data["order_id"]),
            order_date=format_datetime(data.get("order_date", datetime.now())),
            confirmed_order=confirmed_order,
            desired_date=format_datetime(data["desired_date"]),
            deliver_date=format_datetime(data["deliver_date"]),
            deliver_status=deliver_status,
            payment_method=data["payment_method"],
            member_id=format_uuid(data["member_id"]),
            orders=data["orders"],  # dict
            total_fee=safe_int(data.get("total_fee", 0)),
            tax=float(data.get("tax", 0)),
            delivery_fee=safe_float(data.get("delivery_fee", 0)),
            recipient=data["recipient"],
            address=data["address"],
            invoice=safe_int(data.get("invoice", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_date": self.order_date,
            "confirmed_order": (
                self.confirmed_order.name if self.confirmed_order else None
            ),
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
            "total_fee": self.total_fee,
            "tax": self.tax,
            "delivery_fee": self.delivery_fee,
            "recipient": self.recipient,
            "address": self.address,
            "invoice": self.invoice,
        }

    def tax_ratio(self):
        """
        Return the proportion of tax from a tax-included price
        """
        return TAX_RATE / (1 + TAX_RATE)

    def calculate_tax_fee(self, product_map: Dict[str, Product], pid: str) -> float:
        product = product_map.get(pid)
        tax_fee = product.price * self.tax_ratio()
        return tax_fee

    def calculate_fee_detail(self, product_map: Dict[str, Product]) -> Dict[str, float]:
        total_fee = 0
        for pid, qty in self.orders.items():
            product = product_map.get(pid)
            if not product:
                raise ValueError(f"Product ID {pid} not found")
            total_fee += product.price * qty  # price *quantity

        tax_fee = total_fee * self.tax_ratio()
        return {"tax_fee": tax_fee, "total_fee": total_fee}

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
        if self.total_fee < 0:
            raise ValueError("order_fee, total_fee, and tax_rate cannot be negative")
