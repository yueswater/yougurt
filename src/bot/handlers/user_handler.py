# src/bot/handlers/user_handler.py
import uuid
from datetime import datetime
from linebot.models import TextSendMessage
from bot.utils.membership_utils import check_if_user_exists
from linebot import LineBotApi
from models.member import Member
from repos.member_repo import GoogleSheetMemberRepository
import logging

repo = GoogleSheetMemberRepository()

bind_state = {}  # user_id -> dict

def initiate_binding(user_id: str):
    bind_state[user_id] = {"step": "waiting_name"}
    return TextSendMessage(text="請輸入您的本名 👤")

def handle_binding_step(user_id: str, text: str, line_bot_api: LineBotApi):
    state = bind_state.get(user_id)

    if state["step"] == "waiting_name":
        state["name"] = text
        state["step"] = "waiting_phone"
        return TextSendMessage(text="請輸入您的手機號碼 📱")

    elif state["step"] == "waiting_phone":
        state["phone"] = text
        state["step"] = "waiting_confirm"
        name = state["name"]
        phone = state["phone"]
        return TextSendMessage(
            text=(
                f"以下是您輸入的資訊：\n"
                f"👤 姓名：{name}\n"
                f"📱 手機號碼：{phone}\n\n"
                f"請輸入「是」以完成綁定，或輸入「否」重新輸入。"
            )
        )

    elif state["step"] == "waiting_confirm":
        if text == "是":
            # ✅ 檢查是否已綁定
            if check_if_user_exists(user_id):
                bind_state.pop(user_id, None)  # 清除狀態避免卡住
                return TextSendMessage(text="⚠️ 您的帳號已完成綁定，請勿重複註冊。")

            name = state["name"]
            phone = state["phone"]
            return complete_binding(user_id, line_bot_api, name, phone)

        elif text == "否":
            bind_state[user_id] = {"step": "waiting_name"}  # 重設狀態
            return TextSendMessage(text="請重新輸入您的本名 👤")

        else:
            return TextSendMessage(text="請輸入「是」或「否」來確認資訊是否正確")

def complete_binding(user_id: str, line_bot_api, real_name: str, phone: str):
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception as e:
        logging.error("無法取得使用者 %s 的 LINE 資料：%s", user_id, str(e))
        return TextSendMessage(text="無法取得您的 LINE 名稱，請稍後再試")

    member_data = {
        "member_id": str(uuid.uuid4()),
        "line_id": str(user_id),
        "member_name": str(real_name),
        "create_at": datetime.now().isoformat(),
        "order_type": "",
        "remain_delivery": 0,
        "remain_volume": 0,
        "prepaid": 17160
    }

    logging.info("準備儲存會員資料：%s", member_data)
    try:
        member = Member.from_dict(member_data)
        repo.add(member)
        logging.debug(f"已經成功加入會員資料")
    except Exception as e:
        logging.error("會員資料儲存失敗：%s", str(e))
        return TextSendMessage(text="⚠️ 資料儲存失敗，請稍後再試")

    bind_state.pop(user_id, None)
    return TextSendMessage(text=f"您好，{real_name}，已成功綁定會員！")

def is_in_binding_process(user_id: str) -> bool:
    return user_id in bind_state


