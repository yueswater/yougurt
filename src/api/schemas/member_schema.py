from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MemberIn(BaseModel):
    member_id: UUID
    line_id: str
    member_name: str
    create_at: datetime
    order_type: str
    remain_delivery: int
    remain_volume: int
    prepaid: int
