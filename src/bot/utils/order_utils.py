from typing import Dict


def parse_order_items(text: str) -> Dict[str, int]:
    items = text.strip().split("\n")
    order_dict = {}
    for item in items:
        name, count = item.rsplit(" ", 1)
        order_dict[name] = int(count)
    return order_dict
