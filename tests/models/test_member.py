from datetime import datetime
from uuid import uuid4

import pytest

from src.models.member import Member, PaymentStatus


def test_member_valid_data(valid_member):
    assert valid_member.member_name == "測試用戶"
    assert valid_member.balance == 1000


def test_member_negative_remain_delivery():
    with pytest.raises(ValueError) as exc:
        Member(
            member_id=uuid4(),
            line_id="Utest",
            member_name="壞資料",
            create_at=datetime.now(),
            phone="0912345678",
            order_type="once",
            remain_delivery=-1,
            remain_volume=1,
            payment_status=PaymentStatus.UNPAID,
            balance=0,
            valid_member=False,
            remain_free_quota=1,
        )
    assert "remain_delivery cannot be negative" in str(exc.value)


def test_member_negative_balance():
    with pytest.raises(ValueError) as exc:
        Member(
            member_id=uuid4(),
            line_id="Utest",
            member_name="壞資料",
            create_at=datetime.now(),
            phone="0912345678",
            order_type="once",
            remain_delivery=0,
            remain_volume=1,
            payment_status=PaymentStatus.UNPAID,
            balance=-500,
            valid_member=False,
            remain_free_quota=1,
        )
    assert "balance cannot be negative" in str(exc.value)
