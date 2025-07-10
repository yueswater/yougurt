from linebot import LineBotApi
from linebot.models import Message, TextSendMessage

from src.bot import constants
from src.bot.handlers import order_handler, purchase_handler, user_handler

INTERRUPTING_WORDS = list(constants.KEYWORDS.values())


def dispatch(
    user_id: str, text: str, line_bot_api: LineBotApi
) -> Message | list[Message]:
    # 綁定流程
    if user_handler.is_binding_session_active(user_id):
        if text in INTERRUPTING_WORDS and text != constants.KEYWORDS.get("Binding"):
            return TextSendMessage(text="請先完成會員綁定再完成其他操作！")
        if user_handler.member_service.exists(user_id):
            return TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        return user_handler.handle_binding_step(user_id, text, line_bot_api)

    elif text == constants.KEYWORDS.get("Binding", ""):
        if user_handler.member_service.exists(user_id):
            return TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        return user_handler.initiate_binding(user_id)

    # 年購方案流程（NEW）
    elif purchase_handler.purchase_session.is_active(user_id):
        step = purchase_handler.purchase_session.get_session(user_id).get("step")
        if step == "waiting_bank_account":
            return purchase_handler.handle_waiting_bank_account(user_id, text)
        elif step == "waiting_purchase_confirm":
            return purchase_handler.handle_waiting_purchase_confirm(user_id, text)

    elif text == constants.KEYWORDS.get("Purchase", ""):
        return purchase_handler.handle_annual_purchase_start(user_id)

    # 下訂流程
    elif order_handler.is_order_session_active(user_id):
        return order_handler.handle_order_step(user_id, text, line_bot_api)

    elif text == constants.KEYWORDS.get("Order", ""):
        if text in INTERRUPTING_WORDS and text != constants.KEYWORDS.get("Order"):
            return TextSendMessage(text="請先完成下單再完成其他操作！")
        if order_handler.member_service.exists(user_id):
            return order_handler.initiate_order(user_id)
        return TextSendMessage(text="請先完成會員綁定喔～")

    # 其他（預設回覆）
    else:
        return TextSendMessage(text=constants.Message.get("OTHER_NEEDED", ""))
