from linebot import LineBotApi
from linebot.models import Message, TextSendMessage

from src.bot import constants
from src.bot.handlers import order_handler, purchase_handler, user_handler

INTERRUPTING_WORDS = list(constants.KEYWORDS.values())


def dispatch(
    user_id: str, text: str, line_bot_api: LineBotApi
) -> Message | list[Message]:
    # ✅ 防呆機制：如果任一流程正在進行，且輸入了其他流程的關鍵字，則中斷原流程
    if text in INTERRUPTING_WORDS:
        if user_handler.is_binding_session_active(
            user_id
        ) and text != constants.KEYWORDS.get("Binding"):
            user_handler.binding_session.clear_session(user_id)
            return TextSendMessage(text="🔁 已為您中止原本的會員綁定流程，請重新選擇功能")
        if order_handler.is_order_session_active(
            user_id
        ) and text != constants.KEYWORDS.get("Order"):
            order_handler.order_session.clear_session(user_id)
            return TextSendMessage(text="🔁 已為您中止原本的訂購流程，請重新選擇功能")
        if purchase_handler.purchase_session.is_active(
            user_id
        ) and text != constants.KEYWORDS.get("Purchase"):
            purchase_handler.purchase_session.clear_session(user_id)
            return TextSendMessage(text="🔁 已為您中止原本的年購方案流程，請重新選擇功能")

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
        return purchase_handler.handle_annual_purchase_start(user_id)

    # 下訂流程
    elif order_handler.is_order_session_active(user_id):
        return order_handler.handle_order_step(user_id, text, line_bot_api)

    elif text == constants.KEYWORDS.get("Order", ""):
        if order_handler.member_service.exists(user_id):
            return order_handler.initiate_order(user_id)
        return TextSendMessage(text="請先完成會員綁定喔～")

    # 剩餘次數查詢流程
    elif text == constants.KEYWORDS.get("Remain Order", ""):
        if not order_handler.member_service.exists(user_id):
            return TextSendMessage(text="您尚未綁定會員，請先綁定帳號才能查詢剩餘次數。")

        member = order_handler.member_service.get_by_line_id(user_id)
        remain = member.remain_delivery
        prepaid = member.prepaid

        return TextSendMessage(text=f"您目前的剩餘配送次數為：{remain} 次\n訂購額度為：${prepaid}")

    # 預設回覆
    else:
        return TextSendMessage(text=constants.Message.get("OTHER_NEEDED", ""))
