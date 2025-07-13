from datetime import datetime
from uuid import uuid4

import pytest

from src.models.order import DeliverStatus, Order, OrderStatus
from src.models.product import Product


def test_order_valid_data(valid_order):
    assert valid_order.deliver_status == DeliverStatus.DELIVERED


def test_order_calculate_total_fee(valid_order):
    product_map = {
        "P001": Product(
            product_id="P001", product_name="優格原味", price=100, category="優格"
        ),
        "P002": Product(
            product_id="P002", product_name="優格蜂蜜", price=120, category="優格"
        ),
    }
    valid_order.orders = {"P001": 2, "P002": 1}  # 100 * 2 + 120 * 1 = 320
    fee_detail = valid_order.calculate_fee_detail(product_map)
    total = fee_detail["total_fee"]
    assert total == 320 + 320 * valid_order.tax_ratio()


def test_order_negative_total_fee():
    with pytest.raises(ValueError) as exc:
        Order(
            order_id=uuid4(),
            order_date=datetime.now(),
            confirmed_order=OrderStatus.CONFIRMED,
            desired_date=datetime.now(),
            deliver_date=datetime.now(),
            deliver_status=DeliverStatus.DELIVERED,
            payment_method="cash",
            member_id=uuid4(),
            orders={"item": 1},
            order_fee=200,
            total_fee=-10,
            recipient="測試人",
            address="不良地址",
            invoice="INV-001",
            tax=5.3,
        )
    assert "total_fee" in str(exc.value)
