import json
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID

from src.models.order import Order
from src.utils.sheet_client import get_worksheet


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Order]:
        pass

    @abstractmethod
    def get_by_order_id(self, order_id: UUID) -> Optional[Order]:
        pass

    @abstractmethod
    def get_by_member_id(self, member_id: UUID) -> Optional[Order]:
        pass


class GoogleSheetOrderRepository(OrderRepository):
    def __init__(self):
        super().__init__()
        self.worksheet = get_worksheet("Orders")

    def add(self, order: Order) -> None:
        data = order.to_dict()
        row = [
            str(data["order_id"]),
            data["order_date"].isoformat(),
            data["shipping_date"].isoformat(),
            data["shipping_status"],
            data["payment_method"],
            str(data["member_id"]),
            json.dumps(data["orders"]),
            data["order_fee"],
            data["total_fee"],
            data["address"],
            data["invoice"],
            data["tax"],
        ]
        self.worksheet.append_row(row)

    def get_all(self) -> List[Order]:
        rows = self.worksheet.get_all_records()
        orders = []

        for row in rows:
            data = {
                "order_id": row["Order ID"],
                "order_date": row["Order Date"],
                "shipping_date": row["Shipping Date"],
                "shipping_status": row["Shipping Status"],
                "payment_method": row["Payment Method"],
                "member_id": row["Member ID"],
                "orders": json.loads(row["Orders"]),
                "order_fee": row["Order Fee"],
                "total_fee": row["Total Fee"],
                "address": row["Address"],
                "invoice": row["Invoice"],
                "tax": row["Tax"],
            }
            orders.append(Order.from_dict(data))
        return orders

    def get_by_order_id(self, order_id: Union[str, UUID]) -> Optional[Order]:
        all_orders = self.get_all()
        if not isinstance(order_id, UUID):
            order_id = UUID(order_id)

        order = next((o for o in all_orders if o.order_id == order_id), None)
        return order

    def get_by_member_id(self, member_id: Union[str, UUID]) -> List[Order]:
        all_orders = self.get_all()
        if not isinstance(member_id, UUID):
            member_id = UUID(member_id)

        orders = [o for o in all_orders if o.member_id == member_id]
        return orders
