from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID

from src.models.order import Order
from src.repos.product_repo import GoogleSheetProductRepository
from src.utils.sheet_client import get_worksheet


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None:
        pass

    @abstractmethod
    def update(self, order: Order) -> None:
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
        self.product_repo = GoogleSheetProductRepository()

    def add(self, order: Order) -> None:
        data = order.to_dict()

        orders_display = "、".join(
            f"{self.product_repo.get_by_id(pid).product_name} * {qty}"
            for pid, qty in data["orders"].items()
        )

        row = [
            str(data["order_id"]),
            data["order_date"].isoformat(),
            data["confirmed_order"],  # OrderStatus name
            data["desired_date"].isoformat(),
            data["deliver_date"],
            data["deliver_status"],  # DeliverStatus name
            data["payment_method"],
            str(data["member_id"]),
            orders_display,
            str(data["total_fee"]),
            str(data["tax"]),
            str(data["delivery_fee"]),
            data["recipient"],
            data["address"],
            data["invoice"],
        ]
        self.worksheet.append_row(row)

    def get_all(self) -> List[Order]:
        rows = self.worksheet.get_all_records()
        orders = []

        for row in rows:
            data = {
                "order_id": row["Order ID"],
                "order_date": row["Order Date"],
                "confirmed_order": row["Confirmed Order"],
                "desired_date": row["Desired Date"],
                "deliver_date": row["Deliver Date"] or "",
                "deliver_status": row["Deliver Status"],
                "payment_method": row["Payment Method"],
                "member_id": row["Member ID"],
                "orders": {
                    item.split(" * ")[0].strip(): int(item.split(" * ")[1].strip())
                    for item in row["Orders"].split("、")
                    if " * " in item
                },
                "total_fee": row["Total Fee"],
                "tax": float(row["Tax"]),
                "recipient": row["Recipient"],
                "address": row["Address"],
                "invoice": row["Invoice"],
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

    def update(self, updated_order: Order) -> None:
        all_rows = self.worksheet.get_all_records()
        for idx, row in enumerate(all_rows, start=2):
            if row["Order ID"] == str(updated_order.order_id):
                data = updated_order.to_dict()
                data["confirmed_order"] = (
                    data["confirmed_order"].name
                    if hasattr(data["confirmed_order"], "name")
                    else data["confirmed_order"]
                )
                data["deliver_status"] = (
                    data["deliver_status"].name
                    if hasattr(data["deliver_status"], "name")
                    else data["deliver_status"]
                )
                orders_display = "、".join(
                    f"{pid} * {qty}" for pid, qty in data["orders"].items()
                )
                update_row = [
                    str(data["order_id"]),
                    data["order_date"].isoformat(),
                    data["confirmed_order"],
                    data["desired_date"].isoformat(),
                    data["deliver_date"],
                    data["deliver_status"],
                    data["payment_method"],
                    str(data["member_id"]),
                    orders_display,
                    str(data["total_fee"]),
                    str(data["tax"]),
                    str(data["delivery_fee"]),
                    data["recipient"],
                    data["address"],
                    data["invoice"],
                ]
                self.worksheet.update(f"A{idx}:O{idx}", [update_row])  # noqa: E231
                return
        raise ValueError("Order not found")
