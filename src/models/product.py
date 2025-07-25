from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Product:
    product_id: str
    product_name: str
    price: int
    category: str
    available: bool = True

    @classmethod
    def from_dict(cls, data: Dict) -> "Product":
        return cls(
            product_id=data["product_id"],
            product_name=data["product_name"],
            price=data["price"],
            category=data["category"],
            available=data["available"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "category": self.category,
            "available": self.available,
        }

    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("price cannot be negative or zero.")
