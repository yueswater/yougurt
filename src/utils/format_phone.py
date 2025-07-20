def format_phone(phone: str) -> str:
    phone = str(phone).strip()
    if phone.startswith("9") and len(phone) == 9:
        phone = "0" + phone
    if len(phone) == 10:
        return f"{phone[:4]}-{phone[4:7]}-{phone[7:]}"
    return phone
