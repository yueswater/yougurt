import logging
from datetime import datetime, timedelta

from linebot import LineBotApi
from linebot.models import (
    BoxComponent,
    BubbleContainer,
    ButtonComponent,
    ButtonsTemplate,
    DatetimePickerTemplateAction,
    FlexSendMessage,
    MessageAction,
    SeparatorComponent,
    TemplateSendMessage,
    TextComponent,
    TextSendMessage,
)

from src.bot.utils.order_utils import parse_order_items
from src.core.session.order_session_store import OrderSessionStore
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.repos.product_repo import GoogleSheetProductRepository
from src.services.member_service import MemberService
from src.services.order_service import OrderService

order_session = OrderSessionStore()

member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)

order_repo = GoogleSheetOrderRepository()
order_service = OrderService(order_repo)

product_repo = GoogleSheetProductRepository()


def handle_waiting_recipient(line_id: str, text: str) -> TextSendMessage:
    order_session.set_field(line_id, "recipient", text)
    order_session.set_field(line_id, "step", "waiting_address")
    return TextSendMessage(text="請輸入收件人地址")


def handle_waiting_address(line_id: str, text: str) -> TextSendMessage:
    order_session.set_field(line_id, "address", text)
    order_session.set_field(line_id, "step", "waiting_orders")
    return TextSendMessage(text="請輸入「完整」商品名稱與數量，並在不同品項間換行（如下）：\n\n牛奶希臘優格 1\n蜂蜜脆片希臘優格 2")


def handle_waiting_orders(line_id: str, text: str) -> TemplateSendMessage:
    try:
        order_items = parse_order_items(text)
        order_session.set_field(line_id, "orders", order_items)
        order_session.set_field(line_id, "step", "waiting_desired_date")

        return handle_waiting_desired_date(line_id)  # ✅ 直接 return 日期選擇器

    except Exception as e:
        logging.warning("商品解析錯誤：%s", str(e))
        return TextSendMessage(text="格式錯誤，請重新輸入。")


def handle_selected_date(line_id: str, date_str: str) -> FlexSendMessage:
    order_session.set_field(line_id, "desired_date", date_str)
    order_session.set_field(line_id, "step", "waiting_confirm")

    session = order_session.get_session(line_id)
    recipient = session.get("recipient", "")
    address = session.get("address", "")
    orders = session.get("orders", {})
    desired_date = session.get("desired_date", "")

    order_summary_components = [TextComponent(text="商品：", margin="md")]
    for name, qty in orders.items():
        order_summary_components.append(
            TextComponent(text=f"• {name} x {qty}瓶", wrap=True, margin="md")
        )

    return FlexSendMessage(
        alt_text="請確認訂單資訊",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="訂單確認", weight="bold", size="lg"),
                    SeparatorComponent(margin="md"),
                    TextComponent(text=f"收件人：{recipient}", wrap=True, margin="md"),
                    TextComponent(text=f"地址：{address}", wrap=True, margin="md"),
                    *order_summary_components,  # 插入你拆開的商品項目
                    TextComponent(
                        text=f"期望配送日期：{desired_date}", wrap=True, margin="md"
                    ),
                    SeparatorComponent(margin="md"),
                    TextComponent(
                        text="請點選下方按鈕確認是否送出：", size="sm", color="#888888", margin="md"
                    ),
                ],
            ),
            footer=BoxComponent(
                layout="horizontal",
                spacing="md",
                contents=[
                    ButtonComponent(
                        style="primary",
                        color="#00C851",  # 綠色
                        action=MessageAction(label="是", text="是"),
                    ),
                    ButtonComponent(
                        style="primary",
                        color="#ff4444",  # 紅色
                        action=MessageAction(label="否", text="否"),
                    ),
                ],
            ),
        ),
    )


def handle_waiting_desired_date(line_id: str) -> TemplateSendMessage:
    order_session.set_field(line_id, "step", "waiting_confirm")

    return TemplateSendMessage(
        alt_text="請選擇期望配送日期",
        template=ButtonsTemplate(
            title="請選擇期望配送日期",
            text="點選下方按鈕選擇日期",
            actions=[
                DatetimePickerTemplateAction(
                    label="選擇日期",
                    data=f"action=select_date&line_id={line_id}",
                    mode="date",  # 也可以是 "time" 或 "datetime"
                    initial=(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    min=(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    max=(datetime.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
                )
            ],
        ),
    )


def handle_waiting_confirm(
    line_id: str, answer: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    order_session.set_field(line_id, "step", "waiting_confirm")
    if answer == "是":
        try:
            session = order_session.get_session(line_id)
            recipient = session.get("recipient")
            address = session.get("address")
            orders = session.get("orders")

            desired_date = datetime.strptime(session.get("desired_date"), "%Y-%m-%d")

            name_to_pid, product_map = get_product_lookup()
            converted_orders = {}
            for name, qty in orders.items():
                pid = name_to_pid.get(name)
                if not pid:
                    raise ValueError(f"找不到商品名稱：{name}")
                converted_orders[pid] = qty

            # Create an order
            created_order = order_service.create_order(
                line_id=line_id,
                recipient=recipient,
                address=address,
                orders=converted_orders,
                payment_method="LINE",
                desired_date=desired_date,
                product_map=product_map,
            )

            order_session.clear_session(line_id)

            # 建立商品清單區塊
            product_lines = []
            for pid, qty in created_order.orders.items():
                product = product_map.get(pid)
                if product:
                    product_lines.append(
                        TextComponent(
                            text=f"• {product.product_name} x {qty}瓶",
                            size="md",
                            wrap=True,
                            margin="sm",  # 加入這一行
                        )
                    )

            # 訂單詳情 Bubble
            order_detail_bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(text="訂單詳情", weight="bold", size="lg"),
                        SeparatorComponent(margin="md"),
                        TextComponent(
                            text=f"訂單編號：{str(created_order.order_id)[:5]}",
                            wrap=True,
                            margin="md",
                        ),
                        TextComponent(
                            text=f"收件人姓名：{created_order.recipient}",
                            wrap=True,
                            margin="md",
                        ),
                        TextComponent(
                            text=f"地址：{created_order.address}", wrap=True, margin="md"
                        ),
                        TextComponent(text="配送內容：", margin="md"),
                        *product_lines,  # 若太擠可以考慮在 product_lines 中的每一項也加上 margin
                        TextComponent(
                            text=f"額度扣除：${created_order.order_fee}",
                            margin="md",
                            wrap=True,
                        ),
                        TextComponent(
                            text=f"訂購日期：{created_order.order_date.strftime('%Y-%m-%d')}",
                            margin="md",
                            wrap=True,
                        ),
                        TextComponent(
                            text=f"期望配送日期：{created_order.desired_date.strftime('%Y-%m-%d')}",
                            margin="md",
                            wrap=True,
                        ),
                    ],
                )
            )

            return [
                TextSendMessage(text="訂單已建立成功！謝謝您的訂購。"),
                FlexSendMessage(alt_text="訂單詳情", contents=order_detail_bubble),
            ]

        except Exception:
            logging.exception("訂單建立失敗")
            return TextSendMessage(text="訂單建立失敗，請稍後再試")

    elif answer == "否":
        order_session.start_session(line_id)
        return TextSendMessage(text="請重新輸入收件人姓名")
    else:
        order_session.clear_session(line_id)
        return TextSendMessage(text="輸入錯誤，請重新按下「優格訂購」")


def handle_order_step(
    line_id: str, text: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    step = order_session.get_session(line_id).get("step")

    if step == "waiting_recipient":
        return handle_waiting_recipient(line_id, text)
    elif step == "waiting_address":
        return handle_waiting_address(line_id, text)
    elif step == "waiting_orders":
        return handle_waiting_orders(line_id, text)
    elif step == "waiting_desired_date":
        return handle_waiting_desired_date(line_id)
    elif step == "waiting_confirm":
        return handle_waiting_confirm(line_id, text, line_bot_api)
    else:
        order_session.clear_session(line_id)
        return TextSendMessage(text="訂單流程異常，請輸入「開始訂購」重新開始")


def initiate_order(line_id: str) -> TextSendMessage:
    # if not member_service.exists(line_id):
    #     return TextSendMessage(text="您尚未綁定會員，請先綁定會員後再下單。")

    # if not member_service.check_valid_member(line_id):
    #     return TextSendMessage(text="您尚未完成付款，請先付款後等待審核完成。")

    order_session.start_session(line_id)
    return TextSendMessage(text="請輸入收件人姓名")


def is_order_session_active(line_id: str) -> bool:
    return order_session.is_active(line_id)


def get_product_lookup():
    product_list = product_repo.get_all()
    name_to_pid = {p.product_name: p.product_id for p in product_list}
    product_map = {p.product_id: p for p in product_list}
    return name_to_pid, product_map
