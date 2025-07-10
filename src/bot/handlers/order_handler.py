import logging
from datetime import datetime, timedelta

from linebot import LineBotApi
from linebot.models import (
    ButtonsTemplate,
    DatetimePickerTemplateAction,
    MessageAction,
    QuickReply,
    QuickReplyButton,
    TemplateSendMessage,
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
    return TextSendMessage(text="請輸入收件人地址：")


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


def handle_selected_date(line_id: str, date_str: str) -> TextSendMessage:
    order_session.set_field(line_id, "desired_date", date_str)
    order_session.set_field(line_id, "step", "waiting_confirm")

    session = order_session.get_session(line_id)
    recipient = session.get("recipient", "")
    address = session.get("address", "")
    orders = session.get("orders", {})
    desired_date = session.get("desired_date", "")

    orders_summary = (
        "\n".join([f"{name}：{qty}瓶" for name, qty in orders.items()]) if orders else "無"
    )

    confirmation_text = (
        f"以下是您即將送出的訂單資訊：\n\n"
        f"收件人：{recipient}\n"
        f"收件人地址：{address}\n"
        f"商品：\n{orders_summary}\n"
        f"期望配送日期：{desired_date}\n\n"
        f"請點選下方選項以確認訂單："
    )

    return TextSendMessage(
        text=confirmation_text,
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="是", text="是")),
                QuickReplyButton(action=MessageAction(label="否", text="否")),
            ]
        ),
    )


def handle_waiting_desired_date(line_id: str) -> TemplateSendMessage:
    order_session.set_field(line_id, "step", "waiting_confirm")

    return TemplateSendMessage(
        alt_text="請選擇預計配送日期",
        template=ButtonsTemplate(
            title="請選擇預計配送日期",
            text="點選下方按鈕選擇日期",
            actions=[
                DatetimePickerTemplateAction(
                    label="選擇日期",
                    data=f"action=select_date&line_id={line_id}",
                    mode="date",  # 也可以是 "time" 或 "datetime"
                    initial=datetime.today().strftime("%Y-%m-%d"),
                    min=datetime.today().strftime("%Y-%m-%d"),
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
            _ = order_service.create_order(
                line_id=line_id,
                recipient=recipient,
                address=address,
                orders=converted_orders,
                payment_method="LINE",
                desired_date=desired_date,
                product_map=product_map,
            )

            order_session.clear_session(line_id)
            return TextSendMessage(text="訂單已建立成功！謝謝您的訂購。")

        except Exception:
            logging.exception("訂單建立失敗")
            return TextSendMessage(text="訂單建立失敗，請稍後再試")

    elif answer == "否":
        order_session.start_session(line_id)
        return TextSendMessage(text="請重新輸入收件人姓名：")
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
    if not member_service.exists(line_id):
        return TextSendMessage(text="您尚未綁定會員，請先綁定會員後再下單。")

    if not member_service.check_valid_member(line_id):
        return TextSendMessage(text="您尚未完成付款，請先付款後等待審核完成。")

    order_session.start_session(line_id)
    return TextSendMessage(text="請輸入收件人姓名：")


def is_order_session_active(line_id: str) -> bool:
    return order_session.is_active(line_id)


def get_product_lookup():
    product_list = product_repo.get_all()
    name_to_pid = {p.product_name: p.product_id for p in product_list}
    product_map = {p.product_id: p for p in product_list}
    return name_to_pid, product_map
