from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MemberIn(BaseModel):
    member_id: UUID
    line_id: str
    member_name: str
    create_at: datetime
    phone: str
    order_type: str
    remain_delivery: int
    remain_volume: int
    prepaid: int
    valid_member: bool = False


class MemberOut(MemberIn):
    pass


class MemberUpdate(BaseModel):
    member_name: Optional[str] = None
    phone: Optional[str] = None
    remain_delivery: Optional[int] = None
    remain_volume: Optional[int] = None
    valid_member: Optional[bool] = None


class MemberResponse(BaseModel):
    status: str
    data: MemberOut


class MemberBindRequest(BaseModel):
    line_id: str = Field(..., description="使用者的 LINE ID")
    name: str = Field(..., description="會員姓名")
    phone: str = Field(..., description="手機號碼")
    display_name: str | None = Field(None, description="LINE 顯示名稱（後端補上）")
