import logging

from fastapi import APIRouter, HTTPException

from src.api.schemas.member_schema import MemberIn
from src.models.member import Member
from src.repos.member_repo import save_member

router = APIRouter()


@router.post("/")
def save_member_api(member_in: MemberIn):
    try:
        member = Member.from_dict(member_in.model_dump())
        save_member(member.to_dict())
        return {"status": "success", "data": member.to_dict()}
    except Exception as e:
        logging.error(f"Failed in writing data：{e}")
        raise HTTPException(status_code=500, detail="Failed in writing data")
