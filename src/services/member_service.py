import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from src.models.member import Member, PaymentStatus
from src.repos.member_repo import MemberRepository
from src.services.constants import BASIC_CUPS, BASIC_DELIVERY, BASIC_PRICE, MONTHS


@dataclass
class MemberService:
    repo: MemberRepository

    def create_member(
        self, line_id: str, name: str, phone: str, display_name: Optional[str] = None
    ) -> Member:
        basic_fee = BASIC_PRICE * (BASIC_DELIVERY - 1) * MONTHS  # 15840
        balance = BASIC_PRICE * BASIC_DELIVERY * MONTHS  # 17160
        unit_quota = BASIC_PRICE * BASIC_CUPS  # 1320
        member_data = {
            "member_id": str(uuid.uuid4()),
            "line_id": line_id,
            "member_name": name,
            "create_at": datetime.now().isoformat(),
            "phone": phone,
            "order_type": "",
            "remain_delivery": BASIC_DELIVERY,
            "remain_volume": 0,
            "payment_status": PaymentStatus.UNPAID,
            "balance": balance,
            "display_name": display_name,
            "valid_member": False,
            "bank_account": "",
            "remain_free_quota": int(balance // (basic_fee + unit_quota)),
            "total_delivery_fee": 0,
        }
        member = Member.from_dict(member_data)
        self.repo.add(member)
        return member

    def get_by_line_id(self, line_id: str) -> Member:
        return next(m for m in self.repo.get_all() if m.line_id == line_id)

    def exists(self, line_id: str) -> bool:
        return self.repo.exists(line_id)

    def check_valid_member(self, line_id: str) -> bool:
        return self.repo.is_valid_member(line_id)

    def check_member_paid(self, member_id: str) -> bool:
        return self.repo.is_paid(member_id)

    def update_fields_by_line_id(self, line_id: str, updates: dict) -> Member:
        # Find out old membership profiles
        member = self.repo.get_by_line_id(line_id)
        if not member:
            raise ValueError(f"找不到 line_id={line_id} 的會員")

        # Convert dataclass to dict to handle
        member_data = asdict(member)

        updatable_fields = {
            "member_name",
            "phone",
            "order_type",
            "remain_delivery",
            "remain_volume",
            "payment_status",
            "balance",
            "valid_member",
            "bank_account",
            "display_name",
        }

        for field, value in updates.items():
            if field in updatable_fields:
                member_data[field] = value

        # Return to Member
        updated_member = Member.from_dict(member_data)

        # Update to repo
        self.repo.update(updated_member)

        return updated_member
