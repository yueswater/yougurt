import logging

from fastapi import APIRouter, HTTPException

from src.api.constants import Messages
from src.api.schemas.member_schema import MemberIn, MemberResponse, MemberUpdate
from src.api.utils.repo_factory import get_member_repo
from src.api.utils.transform_member import to_domain_member

router = APIRouter()
repo = get_member_repo()


@router.post("/", response_model=MemberResponse)
def save_member_api(member_in: MemberIn):
    try:
        member = to_domain_member(member_in)
        repo.add(member)
        return {"status": "success", "data": member.to_dict()}
    except Exception as e:
        logging.error(f"Failed in writing data：{e}")
        raise HTTPException(status_code=500, detail="Failed in writing data")


@router.get("/by-line-id/{line_id}", response_model=MemberResponse)
def get_member_by_line_id(line_id: str):
    try:
        member = repo.get_by_line_id(line_id)
        if not member:
            raise HTTPException(status_code=404, detail=Messages["USER_NOT_FOUND"])
        return {"status": "success", "data": member.to_dict()}
    except Exception:
        logging.error(f"查詢失敗 line_id={line_id}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=Messages["ERROR"].format(error_type="查詢")
        )


@router.put("/by-line-id/{line_id}", response_model=MemberResponse)
def update_member(line_id: str, update_data: MemberUpdate):
    try:
        member = repo.get_by_line_id(line_id)
        if not member:
            raise HTTPException(status_code=404, detail=Messages["USER_NOT_FOUND"])

        # Update member data
        updates = update_data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(member, field, value)

        repo.update(member)

        return {"status": "success", "data": member.to_dict()}
    except Exception:
        logging.error(f"更新失敗 line_id={line_id}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=Messages["ERROR"].format(error_type="更新")
        )


@router.delete("/by-line-id/{line_id}")
def delete_member(line_id: str):
    try:
        repo.delete(line_id)
        return {"status": "success", "message": f"會員 {line_id} 已標記為無效"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception:
        raise HTTPException(
            status_code=500, detail=Messages["ERROR"].format(error_type="更新")
        )
