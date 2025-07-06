from datetime import datetime
from uuid import uuid4

from src.models.member import Member
from src.repos.member_repo import GoogleSheetMemberRepository


def main():
    repo = GoogleSheetMemberRepository()

    test_member = Member(
        member_id=uuid4(),
        line_id="small_piyan",
        member_name="小屁眼",
        create_at=datetime.now(),
        phone="0912345678",
        order_type="monthly",
        remain_delivery=6,
        remain_volume=12,
        prepaid=3000,
        valid_member=False,
    )

    repo.add(test_member)
    print("測試會員已寫入 Google Sheet！")


if __name__ == "__main__":
    main()
