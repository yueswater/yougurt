from datetime import datetime
from uuid import uuid4

import pytest

from src.models.order import Order
from src.models.product import Product


def test_order_valid_data(valid_order):
    assert valid_order.shipping_status == "pending"


def test_order_calculate_total_fee(valid_order):
    product_map = {
        "P001": Product(product_id="P001", product_name="優格原味", price=100),
        "P002": Product(product_id="P002", product_name="優格蜂蜜", price=120),
    }
    valid_order.orders = {"P001": 2, "P002": 1}  # 100 * 2  # 120 * 1
    total = valid_order.calculate_total_fee(product_map)
    assert total == 320


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
