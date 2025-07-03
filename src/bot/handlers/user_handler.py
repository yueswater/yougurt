# src/bot/handlers/user_handler.py
from datetime import datetime
from linebot.models import TextSendMessage
from linebot import LineBotApi

# 模擬後端儲存邏輯（未來你會換成 gspread）
def save_user_to_backend(user_id: str, display_name: str):
    print("[DEBUG] 假裝已儲存使用者資料：")
    print(f"LINE ID: {user_id}")
    print(f"Name: {display_name}")
    print(f"Created At: {datetime.now().isoformat()}")
    # 預設 order_type 為 normal，其餘初始為 0
    return True

def bind_user_profile(event, line_bot_api: LineBotApi):
    user_id = event.source.user_id
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception as e:
        return TextSendMessage(text="無法取得使用者名稱，請稍後再試")

    # 儲存使用者到資料庫（或 Google Sheet）
    save_user_to_backend(user_id, display_name)

    return TextSendMessage(text=f"您好，{display_name}，您已成功綁定帳號！")
