import logging

from linebot import LineBotApi
from linebot.models import TextSendMessage

from repos.member_repo import GoogleSheetMemberRepository
from repos.order_repo import GoogleSheetOrderRepository
from src.bot.utils.order_utils import parse_order_items
from src.core.session.order_session_store import OrderSessionStore
from src.services.member_service import MemberService

order_session = OrderSessionStore()
order_repo = GoogleSheetOrderRepository()
member_repo = GoogleSheetMemberRepository()
member_service = MemberService(member_repo)


def initiate_order(line_id: str) -> TextSendMessage:
    if not member_service.exists(line_id):
        return TextSendMessage(text="⚠️ 您尚未綁定會員，請先綁定會員後再下單。")

    if not member_service.check_valid_member(line_id):
        return TextSendMessage(text="⚠️ 您尚未完成付款，請先付款後等待審核完成。")

    order_session.start_session(line_id)
    return TextSendMessage(text="請輸入收件人姓名：")


def handle_order_step(
    line_id: str, text: str, line_bot_api: LineBotApi
) -> TextSendMessage:
    session = order_session.get_session(line_id)
    step = session.get("step")

    if step == "waiting_recipient":
        order_session.set_field(line_id, "recipient", text)
        order_session.set_field(line_id, "step", "waiting_address")
        return TextSendMessage(text="請輸入收件人地址：")

    elif step == "waiting_address":
        order_session.set_field(line_id, "address", text)
        order_session.set_field(line_id, "step", "waiting_orders")
        return TextSendMessage(text="請輸入商品名稱與數量（例如：\n牛奶 1\n蜂蜜 2）：")

    elif step == "waiting_orders":
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
            return TextSendMessage(text="❗️輸入格式錯誤，請重新輸入商品名稱與數量。格式例如：\n牛奶 1\n蜂蜜 2")

    elif step == "waiting_confirm":
        if text == "是":
            pass
            # TODO: 將訂單寫入 Google Sheet
            order_session.clear_session(line_id)
            return TextSendMessage(text="✅ 訂單已建立成功！謝謝您的訂購。")
        elif text == "否":
            order_session.start_session(line_id)
            return TextSendMessage(text="請重新輸入收件人姓名：")
        else:
            return TextSendMessage(text="請輸入「是」或「否」來確認訂單。")

    return TextSendMessage(text="訂單流程異常，請重新開始。")
