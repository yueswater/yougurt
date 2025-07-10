from linebot.models import TextSendMessage

from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.services.member_service import MemberService

# 初始化服務
member_service = MemberService(GoogleSheetMemberRepository())
order_repo = GoogleSheetOrderRepository()


def handle_order_history(line_id: str) -> TextSendMessage:
    # 1. 檢查是否為有效會員
    if not member_service.exists(line_id):
        return TextSendMessage(text="❗ 請先完成會員綁定，才能查詢訂購紀錄喔～")

    # 2. 取得會員資料（member_id）
    member = member_service.get_by_line_id(line_id)
    member_id = member.member_id

    # 3. 查詢訂購紀錄
    orders = order_repo.get_by_member_id(member_id)

    if not orders:
        return TextSendMessage(text="目前尚無任何訂購紀錄喔～")

    # 4. 整理訂單資料
    lines = ["您的訂購紀錄如下：\n"]
    for order in orders[-5:]:  # 僅顯示最近 5 筆
        order_summary = "、".join(
            [f"{name} * {qty}" for name, qty in order.orders.items()]
        )
        lines.append(f"🗓 {order.order_date.strftime('%Y-%m-%d')}\n商品：{order_summary}\n")

    return TextSendMessage(text="\n".join(lines))
