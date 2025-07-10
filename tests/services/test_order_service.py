from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.models.order import Order
from src.models.product import Product
from src.repos.order_repo import OrderRepository
from src.services.order_service import OrderService


class FakeOrderRepo(OrderRepository):
    def __init__(self):
        self.saved_orders = []

    def add(self, order: Order) -> None:
        self.saved_orders.append(order)

    def get_all(self) -> List[Order]:
        return self.saved_orders

    def get_by_order_id(self, order_id: UUID) -> Optional[Order]:
        return next((o for o in self.saved_orders if o.order_id == order_id), None)

    def get_by_member_id(self, member_id: UUID) -> List[Order]:
        return [o for o in self.saved_orders if o.member_id == member_id]

    def update(self, order: Order) -> None:
        for i, o in enumerate(self.saved_orders):
            if o.order_id == order.order_id:
                self.saved_orders[i] = order
                return


# Simulation data
fake_product_map = {
    "milk": Product(product_id="milk", product_name="牛奶", price=100),
    "honey": Product(product_id="honey", product_name="蜂蜜", price=200),
}


def test_create_order():
    # Arrange
    fake_repo = FakeOrderRepo()
    service = OrderService(repo=fake_repo)

    line_id = "test-line-id"
    recipient = "王小明"
    address = "台北市測試路1號"
    orders = {"milk": 2, "honey": 1}
    payment_method = "LINE PAY"
    desired_date = datetime(2025, 7, 10)

    # mock get_by_line_id() (You may use mock.patch in your real environment)
    from src.services.member_service import MemberService

    class FakeMember:
        member_id = uuid4()

    MemberService.get_by_line_id = lambda self, line_id: FakeMember()

    # Act
    order = service.create_order(
        line_id=line_id,
        recipient=recipient,
        address=address,
        orders=orders,
        payment_method=payment_method,
        desired_date=desired_date,
        product_map=fake_product_map,
    )

    # Assert
    assert order.recipient == recipient
    assert order.orders == orders
    assert (
        order.total_fee == 100 * 2 + 200 * 1 + (100 * 2 + 200 * 1) * order.tax_ratio()
    )
    assert order.confirmed_order.name == "PENDING"
    assert len(fake_repo.saved_orders) == 1

    print("測試成功，建立的訂單如下：")
    print(order.to_dict())


if __name__ == "__main__":
    test_create_order()
