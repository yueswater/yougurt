from linebot.models import TextSendMessage

from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.services.member_service import MemberService

# 初始化 repo 與 service
order_repo = GoogleSheetOrderRepository()
member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


def handle_order_history(line_id: str):
    # 檢查是否為已綁定會員
    if not member_service.exists(line_id):
        return TextSendMessage(text="請先完成會員綁定才能查詢訂購紀錄喔～")

    member = member_service.get_by_line_id(line_id)
    orders = order_repo.get_by_member_id(member.member_id)

    # 過濾掉 Deliver Date 為空的訂單
    filtered_orders = [o for o in orders if o.deliver_date.strftime("%Y-%m-%d").strip()]

    if not filtered_orders:
        return TextSendMessage(text="目前尚無完成配送的訂單紀錄喔～")

    # 組成每筆訂單的顯示文字
    order_texts = [
        f"📦 配送日期：{o.deliver_date}\n內容：{', '.join([f'{k} {v}瓶' for k, v in o.orders.items()])}"
        for o in filtered_orders
    ]

    # 將多筆紀錄合併為單一訊息傳送
    return TextSendMessage(text="\n\n".join(order_texts))
