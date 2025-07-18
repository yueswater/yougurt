def calculate_invoice_amount(
    remaining_balance: int, order_amount: int, free_quota: int = 1320
) -> int:
    invoice_amount = 0

    start = remaining_balance
    end = remaining_balance - order_amount + 1  # 從高往低扣

    # 付費區間是餘額 > 1320
    paid_start = max(end, free_quota + 1)
    paid_end = min(start, 999999)  # 不限制上限

    if paid_start <= paid_end:
        invoice_amount = paid_end - paid_start + 1

    # 超過總點數額度（餘額為負）
    if end < 1:
        invoice_amount += 1 - end

    return invoice_amount
