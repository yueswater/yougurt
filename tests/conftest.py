from datetime import datetime
from uuid import uuid4

import pytest

from src.models.member import Member
from src.models.order import DeliverStatus, Order, OrderStatus


@pytest.fixture
def valid_member():
    return Member(
        member_id=uuid4(),
        line_id="Utest",
        member_name="測試用戶",
        create_at=datetime.now(),
        phone="0912345678",
        order_type="monthly",
        remain_delivery=4,
        remain_volume=12,
        prepaid=1000,
        valid_member=False,
    )


@pytest.fixture
def valid_order(valid_member):
    return Order(
        order_id=uuid4(),
        order_date=datetime.now(),
        confirmed_order=OrderStatus.CONFIRMED,
        desired_date=datetime.now(),
        deliver_date=datetime.now(),
        deliver_status=DeliverStatus.DELIVERED,
        payment_method="cash",
        member_id=valid_member.member_id,
        orders={"A": 1},
        total_fee=110,
        tax=5.28,
        recipient="測試人",
        address="somewhere",
        invoice="INV123",
    )
