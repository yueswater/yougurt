from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.product import Product
from src.utils.sheet_client import get_worksheet


class ProductRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Product]:
        ...

    @abstractmethod
    def get_by_id(self, product_id: str) -> Optional[Product]:
        ...

    @abstractmethod
    def get_by_name(self, product_name: str) -> Optional[Product]:
        ...


class GoogleSheetProductRepository(ProductRepository):
    def __init__(self):
        self.worksheet = get_worksheet("Products")

    def get_all(self) -> List[Product]:
        rows = self.worksheet.get_all_records()
        products = []

        for row in rows:
            data = {
                "product_id": row["Product ID"],
                "product_name": row["Product Name"],
                "price": row["Price"],
                "category": row["Category"],
                "available": row["Available"],
            }
            products.append(Product.from_dict(data))
        return products

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return next((p for p in self.get_all() if p.product_id == product_id), None)

    def get_by_name(self, product_name: str) -> Optional[Product]:
        return next((p for p in self.get_all() if p.product_name == product_name), None)

    def is_available(self, product_id: str) -> Optional[bool]:
        product = self.get_by_id(product_id)
        return product.available if product else None
