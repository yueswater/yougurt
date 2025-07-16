import pytest

from src.models.product import Product


def test_product_valid():
    product = Product(
        product_id="P001",
        product_name="優格原味",
        price=100,
        category="優格",
        available=False,
    )
    assert product.product_id == "P001"
    assert product.price == 100


def test_product_zero_price():
    with pytest.raises(ValueError) as exc:
        Product(
            product_id="P002",
            product_name="試用品",
            price=0,
            category="優格",
            available=False,
        )
    assert "price cannot be negative or zero" in str(exc.value)


def test_product_negative_price():
    with pytest.raises(ValueError) as exc:
        Product(
            product_id="P003",
            product_name="錯誤商品",
            price=-50,
            category="優格",
            available=False,
        )
    assert "price cannot be negative or zero" in str(exc.value)
