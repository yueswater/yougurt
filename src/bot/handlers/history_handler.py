from linebot.models import (
    BoxComponent,
    BubbleContainer,
    CarouselColumn,
    CarouselTemplate,
    FlexSendMessage,
    PostbackAction,
    SeparatorComponent,
    TemplateSendMessage,
    TextComponent,
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


def handle_order_detail(line_id: str, order_id: str) -> FlexSendMessage:
    if not history_session.is_active(line_id):
        return TextSendMessage(text="⚠️ 無法辨識的操作，請先從『訂購紀錄』功能進入")

    if not member_service.exists(line_id):
        return TextSendMessage(text="您尚未綁定會員，請先綁定帳號才能查詢訂購紀錄。")
    elif not member_service.check_valid_member(line_id):
        return TextSendMessage(text="您尚未完成付款，請先付款後等待審核完成。")

    order = order_repo.get_by_order_id(order_id)
    if not order:
        return TextSendMessage(text="❌ 找不到這筆訂單")

    # 產品資訊逐條列出
    product_lines = [
        TextComponent(text=f"∙ {name} x {qty}瓶", size="md", color="#555555")
        for name, qty in order.orders.items()
    ]

    # 建立整體內容
    contents = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="訂單詳情", weight="bold", size="lg"),
                SeparatorComponent(margin="md"),
                TextComponent(text=f"訂單編號：{str(order.order_id)[:5]}", wrap=True),
                TextComponent(text=f"收件人：{order.recipient}", wrap=True),
                TextComponent(text=f"地址：{order.address}", wrap=True),
                TextComponent(text="配送內容：", margin="md"),
                *product_lines,
                SeparatorComponent(margin="md"),
                TextComponent(text=f"額度扣除：{order.order_fee}"),
                TextComponent(text=f"訂購日期：{order.order_date.strftime('%Y-%m-%d')}"),
                TextComponent(text=f"期望配送：{order.desired_date.strftime('%Y-%m-%d')}"),
                TextComponent(
                    text=f"到貨日期：{order.deliver_date.strftime('%Y-%m-%d')}"
                    if order.deliver_date
                    else "到貨日期："
                ),
                TextComponent(text=f"訂單狀態：{order.confirmed_order.name}"),
                TextComponent(text=f"配送狀態：{order.deliver_status.name}"),
            ],
        )
    )

    return FlexSendMessage(alt_text="這是您的訂單詳情", contents=contents)
