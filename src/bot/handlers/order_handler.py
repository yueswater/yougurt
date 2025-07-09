import logging
from datetime import datetime

from linebot import LineBotApi
from linebot.models import TextSendMessage

from src.bot.utils.order_utils import parse_order_items
from src.core.session.order_session_store import OrderSessionStore
from src.models.product import Product
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.services.member_service import MemberService
from src.services.order_service import OrderService

order_session = OrderSessionStore()

member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)

order_repo = GoogleSheetOrderRepository()
order_service = OrderService(order_repo)

product_map = {
    "milk": Product(product_id="milk", product_name="牛奶", price=100),
    "honey": Product(product_id="honey", product_name="蜂蜜", price=200),
}


def handle_waiting_recipient(line_id: str, text: str) -> TextSendMessage:
    order_session.set_field(line_id, "recipient", text)
    order_session.set_field(line_id, "step", "waiting_address")
    return TextSendMessage(text="請輸入收件人地址：")


def handle_waiting_address(line_id: str, text: str) -> TextSendMessage:
    order_session.set_field(line_id, "address", text)
    order_session.set_field(line_id, "step", "waiting_orders")
    return TextSendMessage(text="請輸入商品名稱與數量（例如：\n牛奶 1\n蜂蜜 2）：")


def handle_waiting_orders(line_id: str, text: str) -> TextSendMessage:
    try:
        order_items = parse_order_items(text)
        order_session.set_field(line_id, "orders", order_items)
        order_session.set_field(line_id, "step", "waiting_confirm")

        summary = "\n".join([f"{k}：{v}瓶" for k, v in order_items.items()])
        return TextSendMessage(
            text=f"以下是您輸入的訂單資訊：\n{summary}\n\n請輸入「是」以確認訂單，或輸入「否」重新開始。"
        )
    except Exception as e:
        logging.warning("商品解析錯誤：%s", str(e))
        return TextSendMessage(text="輸入格式錯誤，請重新輸入商品名稱與數量。格式例如：\n牛奶 1\n蜂蜜 2")


def handle_waiting_confirm(
    line_id: str, answer: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    if answer == "是":
        try:
            session = order_session.get_session(line_id)
            recipient = session.get("recipient")
            address = session.get("address")
            orders = session.get("orders")

            desired_date = datetime.now()

            # Create an order
            _ = order_service.create_order(
                line_id=line_id,
                recipient=recipient,
                address=address,
                orders=orders,
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
        return TextSendMessage(text="請輸入「是」或「否」來確認訂單。")


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
