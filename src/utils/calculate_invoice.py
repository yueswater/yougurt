import numpy as np

from src.services.constants import BASIC_CUPS, BASIC_PRICE


def calculate_invoice_amount(
    remaining_balance: int,
    order_amount: int,
    free_quota: int = BASIC_CUPS * BASIC_PRICE,
) -> int:
    # Case 1: 餘額已經是負數，直接全額開發票
    if remaining_balance < 0:
        return order_amount

    start = remaining_balance
    end = remaining_balance - order_amount + 1  # 扣點是從高往低扣

    invoice_amount = 0

    # Case 2: 跨過免費額度 → 要開發票的區段：1321 ~ start
    paid_start = max(end, free_quota + 1)
    paid_end = min(start, np.inf)  # 保險做法

    if paid_start <= paid_end:
        invoice_amount += paid_end - paid_start + 1

    # Case 3: 如果訂單跨過 0，表示超支 → 補開額外發票
    if end < 1:
        invoice_amount += 1 - end  # 超過的那段額外金額也要加進來

    return invoice_amount
