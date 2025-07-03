from datetime import datetime
from uuid import uuid4

import pytest

from src.models.member import Member
from src.models.order import Order


@pytest.fixture
def valid_member():
    return Member(
        member_id=uuid4(),
        line_id="Utest",
        member_name="測試用戶",
        create_at=datetime.now(),
        order_type="monthly",
        remain_delivery=4,
        remain_volume=12,
        prepaid=1000,
    )


@pytest.fixture
def valid_order(valid_member):
    return Order(
        order_id=uuid4(),
        order_date=datetime.now(),
        shipping_date=datetime.now(),
        shipping_status="pending",
        payment_method="cash",
        member_id=valid_member.member_id,
        orders={"A": 1},
        order_fee=100,
        total_fee=110,
        address="somewhere",
        invoice="A000000000",
        tax=10,
    )
