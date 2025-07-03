from datetime import datetime
from uuid import uuid4

import pytest

from src.models.member import Member


def test_member_valid_data(valid_member):
    assert valid_member.member_name == "測試用戶"
    assert valid_member.prepaid == 1000


def test_member_negative_remain_delivery():
    with pytest.raises(ValueError) as exc:
        Member(
            member_id=uuid4(),
            line_id="Utest",
            member_name="壞資料",
            create_at=datetime.now(),
            order_type="once",
            remain_delivery=-1,
            remain_volume=1,
            prepaid=0,
        )
    assert "remain_delivery cannot be negative" in str(exc.value)


def test_member_negative_prepaid():
    with pytest.raises(ValueError) as exc:
        Member(
            member_id=uuid4(),
            line_id="Utest",
            member_name="壞資料",
            create_at=datetime.now(),
            order_type="once",
            remain_delivery=0,
            remain_volume=1,
            prepaid=-500,
        )
    assert "prepaid cannot be negative" in str(exc.value)
