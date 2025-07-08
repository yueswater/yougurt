import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from src.models.order import DeliverStatus, Order, OrderStatus
from src.models.product import Product
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import OrderRepository
from src.services.member_service import MemberService

member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


@dataclass
class OrderService:
    repo: OrderRepository

    def create_order(
        self,
        line_id: str,
        recipient: str,
        address: str,
        orders: Dict[str, int],
        payment_method: str,
        desired_date: datetime,
        product_map: Dict[str, Product],
    ) -> Order:
        now = datetime.now()
        member_id = member_service.get_by_line_id(line_id).member_id

        order = Order(
            order_id=uuid.uuid4(),
            order_date=now,
            confirmed_order=OrderStatus.PENDING,
            desired_date=desired_date,
            deliver_date=None,
            deliver_status=DeliverStatus.PREPARE,
            payment_method=payment_method,
            member_id=member_id,
            orders=orders,
            order_fee=0,
            total_fee=0,
            recipient=recipient,
            address=address,
            invoice="",
        )

        fee_detail = order.calculate_fee_detail(product_map)
        order.order_fee = fee_detail["order_fee"]
        order.total_fee = fee_detail["total_fee"]

        self.repo.add(order)
        return order
