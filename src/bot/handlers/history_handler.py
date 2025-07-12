from linebot.models import (
    CarouselColumn,
    CarouselTemplate,
    PostbackAction,
    TemplateSendMessage,
    TextSendMessage,
)

from src.core.session.history_session_store import HisotrySessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.services.member_service import MemberService

# 初始化 session store
history_session = HisotrySessionStore()

# 初始化 repo 與 service
order_repo = GoogleSheetOrderRepository()
member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


def handle_order_history(line_id: str):
    if not member_service.exists(line_id):
        return TextSendMessage(text="請先完成會員綁定才能查詢訂購紀錄喔～")

    history_session.start_session(line_id)

    member = member_service.get_by_line_id(line_id)
    orders = order_repo.get_by_member_id(member.member_id)

    # 改為依據 order_date 排序
    filtered_orders = sorted(
        [o for o in orders if o.order_date is not None],
        key=lambda o: o.order_date,
        reverse=True,
    )[:10]

    if not filtered_orders:
        return TextSendMessage(text="目前尚無完成配送的訂單紀錄喔～")

    # 建立 Carousel 卡片內容
    columns = []
    for o in filtered_orders:
        order_id_short = str(o.order_id)[:5]
        order_date = o.order_date.strftime("%Y-%m-%d")
        confirm_status = (
            o.confirmed_order.name
            if hasattr(o.confirmed_order, "name")
            else o.confirmed_order
        )
        deliver_status = (
            o.deliver_status.name
            if hasattr(o.deliver_status, "name")
            else o.deliver_status
        )

        text = (
            f"訂單編號前五碼：{order_id_short}\n"
            f"訂購日期：{order_date}\n"
            f"訂單狀態：{confirm_status}\n"
            f"運送狀態：{deliver_status}"
        )

        column = CarouselColumn(
            text=text[:60],  # 最多 60 字元限制
            title="📦 訂單紀錄",
            actions=[
                PostbackAction(
                    label="查看訂單詳情",
                    data=f"order_detail_{o.order_id}",  # ←這個 data 一定要和上面對應的 prefix 一致
                    display_text="查看訂單詳情",
                )
            ],
        )
        columns.append(column)

    return TemplateSendMessage(
        alt_text="這是您的歷史訂單紀錄",
        template=CarouselTemplate(columns=columns),
    )


def handle_order_detail(line_id: str, order_id: str) -> TextSendMessage:
    if not history_session.is_active(line_id):
        return TextSendMessage(text="⚠️ 無法辨識的操作，請先從『訂購紀錄』功能進入")

    if not member_service.exists(line_id):
        return TextSendMessage(text="請先完成會員綁定才能查詢訂單詳情喔～")

    order = order_repo.get_by_order_id(order_id)
    if not order:
        return TextSendMessage(text="❌ 找不到這筆訂單")

    # 格式化內容
    order_lines = [
        f"訂單編號：{order.order_id}",
        f"收件人姓名：{order.recipient}",
        f"地址：{order.address}",
        "配送內容：",
    ]
    for name, qty in order.orders.items():
        order_lines.append(f"　{name} x {qty}瓶")
    order_lines += [
        f"額度扣除：{order.order_fee}",
        f"訂購日期：{order.order_date.strftime('%Y-%m-%d')}",
        f"訂單狀態：{order.confirmed_order.name}",
        f"配送狀態：{order.deliver_status.name}",
    ]

    return TextSendMessage(text="\n".join(order_lines))
