import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from src.models.order import DeliverStatus, Order, OrderStatus
from src.models.product import Product
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import OrderRepository
from src.services.constants import BASIC_DELIVERY_FEE
from src.services.member_service import MemberService
from src.utils.calculate_invoice import calculate_invoice_amount

member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


@dataclass
class OrderService:
    order_repo: OrderRepository

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

        remain_delivery = member_repo.get_remain_delivery_by_id(member_id)
        delivery_fee = 0 if remain_delivery > 0 else BASIC_DELIVERY_FEE

        # Create new order
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
            total_fee=0,
            tax=0.0,
            delivery_fee=delivery_fee,
            recipient=recipient,
            address=address,
            invoice="",
        )

        fee_detail = order.calculate_fee_detail(product_map)
        order.tax = fee_detail["tax_fee"]
        order.total_fee = fee_detail["total_fee"]

        # Update Member data
        member = member_repo.get_by_member_id(member_id=member_id)
        prev_balance = member.balance

        member.balance = (
            prev_balance - order.total_fee
        )  # allow negative balance -> Negative number is the difference
        member.remain_delivery -= 1  # 1

        member_repo.update(member)

        invoice_amount = calculate_invoice_amount(
            remaining_balance=member.balance, order_amount=order.total_fee
        )

        order.invoice = invoice_amount

        self.order_repo.add(order)
        return order
