import numpy as np

from src.services.constants import BASIC_CUPS, BASIC_PRICE


def calculate_invoice_amount(
    remaining_balance: int,
    order_amount: int,
    free_quota: int = BASIC_CUPS * BASIC_PRICE,
) -> int:
    if remaining_balance < 0:
        return order_amount

    start = remaining_balance
    end = remaining_balance - order_amount + 1

    invoice_amount = 0

    paid_start = max(end, free_quota + 1)
    paid_end = min(start, np.inf)
    if paid_start <= paid_end:
        invoice_amount += paid_end - paid_start + 1

    if end < 1:
        invoice_amount += 1 - end

    return invoice_amount
