def test_add_member_should_call_append_row():
    from datetime import datetime
    from unittest.mock import MagicMock
    from uuid import uuid4

    from src.models.member import Member, PaymentStatus
    from src.repos.member_repo import GoogleSheetMemberRepository

    member = Member(
        member_id=uuid4(),
        line_id="Utest123",
        member_name="測試會員",
        create_at=datetime.now(),
        phone="0912345678",
        order_type="monthly",
        remain_delivery=3,
        remain_volume=12,
        payment_status=PaymentStatus.UNPAID,
        balance=1000,
        valid_member=False,
        remain_free_quota=1,
    )

    repo = GoogleSheetMemberRepository.__new__(GoogleSheetMemberRepository)
    repo.worksheet = MagicMock()
    repo.add(member)

    repo.worksheet.append_row.assert_called_once()
