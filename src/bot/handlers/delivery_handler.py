from linebot.models import TextSendMessage

from src.core.session.delivery_session_store import DeliverySessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.services.member_service import MemberService

delivery_session = DeliverySessionStore()
member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


def handle_check_quota(line_id: str):
    if not member_service.exists(line_id):
        return TextSendMessage(text="您尚未綁定會員，請先完成會員綁定。")

    member = member_service.get_by_line_id(line_id)
    remain = member.remain_delivery
    prepaid = member.prepaid

    delivery_session.clear_session(line_id)
    return TextSendMessage(text=f"📦 您目前剩餘配送次數為 {remain} 次，已預付金額為 {prepaid} 元。")
