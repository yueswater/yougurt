from linebot import LineBotApi
from linebot.models import Message, TextSendMessage

from src.bot import constants
from src.bot.handlers import (
    contact_handler,
    delivery_handler,
    history_handler,
    order_handler,
    purchase_handler,
    user_handler,
)

INTERRUPTING_WORDS = list(constants.KEYWORDS.values())


def dispatch(
    user_id: str, text: str, line_bot_api: LineBotApi
) -> Message | list[Message]:
    # ✅ 防呆機制：如果任一流程正在進行，且輸入了其他流程的關鍵字，則中斷原流程
    if text in INTERRUPTING_WORDS:
        if user_handler.is_binding_session_active(user_id):
            user_handler.binding_session.clear_session(user_id)
            # return TextSendMessage(text="🔁 已為您中止原本的會員綁定流程，請重新選擇功能")
        if order_handler.is_order_session_active(user_id):
            order_handler.order_session.clear_session(user_id)
            # return TextSendMessage(text="🔁 已為您中止原本的訂購流程，請重新選擇功能")
        if purchase_handler.purchase_session.is_active(user_id):
            purchase_handler.purchase_session.clear_session(user_id)
            # return TextSendMessage(text="🔁 已為您中止原本的年購方案流程，請重新選擇功能")
        if history_handler.history_session.is_active(user_id):
            history_handler.history_session.clear_session(user_id)

    # 綁定流程
    if user_handler.is_binding_session_active(user_id):
        if user_handler.member_service.exists(user_id):
            return TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        return user_handler.handle_binding_step(user_id, text, line_bot_api)

    elif text == constants.KEYWORDS.get("Binding", ""):
        if user_handler.member_service.exists(user_id):
            return TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        return user_handler.initiate_binding(user_id)

    # 年購方案流程
    elif purchase_handler.purchase_session.is_active(user_id):
        step = purchase_handler.purchase_session.get_session(user_id).get("step")
        if step == "waiting_bank_account":
            return purchase_handler.handle_waiting_bank_account(user_id, text)
        elif step == "waiting_purchase_confirm":
            return purchase_handler.handle_waiting_purchase_confirm(user_id, text)

    elif text == constants.KEYWORDS.get("Purchase", ""):
        if not purchase_handler.member_service.exists(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_MEMBER", "")
            )
        else:
            return purchase_handler.handle_annual_purchase_start(user_id)

    # 下訂流程
    elif order_handler.is_order_session_active(user_id):
        return order_handler.handle_order_step(user_id, text, line_bot_api)

    elif text == constants.KEYWORDS.get("Order", ""):
        if not order_handler.member_service.exists(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_MEMBER", "")
            )
        elif not order_handler.member_service.check_valid_member(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_PAY", "")
            )
        else:
            return order_handler.initiate_order(user_id)

    # 剩餘次數查詢流程
    elif text == constants.KEYWORDS.get("Remain Order", ""):
        if not delivery_handler.member_service.exists(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_MEMBER", "")
            )
        elif not delivery_handler.member_service.check_valid_member(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_PAY", "")
            )
        else:
            return delivery_handler.handle_check_quota(user_id)

    # 聯絡我們流程
    elif text == constants.KEYWORDS.get("Contact", ""):
        return contact_handler.handle_contact_us()

    elif text == constants.KEYWORDS.get("History", ""):
        if not history_handler.member_service.exists(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_MEMBER", "")
            )
        elif not history_handler.member_service.check_valid_member(user_id):
            return TextSendMessage(
                text=constants.MEMBERSHIP_KEYWORDS.get("NOT_PAY", "")
            )
        else:
            return history_handler.handle_order_history(user_id)

    elif text.startswith(constants.KEYWORDS.get("ORDER_INFO", "")):
        order_id = text.replace(constants.KEYWORDS.get("ORDER_INFO", ""), "")
        return history_handler.handle_order_detail(user_id, order_id)

    # 預設回覆
    else:
        return TextSendMessage(text=constants.Message.get("OTHER_NEEDED", ""))


def dispatch_postback(user_id: str, data: str, line_bot_api: LineBotApi):
    if data.startswith("order_detail_"):
        order_id = data.replace("order_detail_", "")
        return history_handler.handle_order_detail(user_id, order_id)

    return TextSendMessage(text="❌ 無法辨識的操作，請再試一次")
