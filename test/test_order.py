from datetime import datetime
from uuid import uuid4

import pytest

from src.models.order import Order


def test_order_valid_data(valid_order):
    assert valid_order.shipping_status == "pending"


def test_order_negative_total_fee():
    with pytest.raises(ValueError) as exc:
        Order(
            order_id=uuid4(),
            order_date=datetime.now(),
            shipping_date=datetime.now(),
            shipping_status="shipped",
            payment_method="cash",
            member_id=uuid4(),
            orders={"item": 1},
            order_fee=200,
            total_fee=-10,
            address="不良地址",
            invoice="X000000001",
            tax=10,
        )
    assert "total_fee" in str(exc.value)
