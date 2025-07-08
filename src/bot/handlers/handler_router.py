from linebot import LineBotApi
from linebot.models import TextSendMessage

from src.bot import constants
from src.bot.handlers import order_handler, user_handler


def dispatch(user_id: str, text: str, line_bot_api: LineBotApi) -> TextSendMessage:
    if user_handler.is_binding_session_active(user_id):
        if user_handler.member_service.exists(user_id):
            return TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        return user_handler.handle_binding_step(user_id, text, line_bot_api)

    elif order_handler.is_order_session_active(user_id):
        return order_handler.handle_order_step(user_id, text, line_bot_api)

    elif text == "綁定會員":
        if user_handler.member_service.exists(user_id):
            return TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        return user_handler.initiate_binding(user_id)

    elif text == "優格訂購":
        if order_handler.member_service.exists(user_id):
            return order_handler.initiate_order(user_id)
        return TextSendMessage(text="請先完成會員綁定喔～")

    # 可擴充更多：查詢訂單、聯絡客服、查詢運費
    else:
        return TextSendMessage(text=constants.Message.get("OTHER_NEEDED", ""))
