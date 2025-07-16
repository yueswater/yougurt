import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from src.models.member import Member, PaymentStatus
from src.repos.member_repo import MemberRepository
from src.services.constants import BASIC_DELIVERY, BASIC_PRICE, MONTHS


@dataclass
class MemberService:
    repo: MemberRepository

    def create_member(
        self, line_id: str, name: str, phone: str, display_name: Optional[str] = None
    ) -> Member:
        basic_fee = BASIC_PRICE * BASIC_DELIVERY * MONTHS
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
            "prepaid": basic_fee,
            "display_name": display_name,
            "valid_member": False,
            "bank_account": "",
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
            "prepaid",
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
