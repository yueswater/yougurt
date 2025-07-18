import numpy as np


def calculate_invoice_amount(
    remaining_balance: int, order_amount: int, free_quota: int = 1320
) -> int:
    invoice_amount = 0

    start = remaining_balance
    end = remaining_balance - order_amount + 1  # Deduct from high to low

    # Paid range is balance > 1320
    paid_start = max(end, free_quota + 1)
    paid_end = min(start, np.inf)  # No limit

    if paid_start <= paid_end:
        invoice_amount = paid_end - paid_start + 1

    # exceeds the total point amount (balance is negative)
    if end < 1:
        invoice_amount += 1 - end

    return invoice_amount
