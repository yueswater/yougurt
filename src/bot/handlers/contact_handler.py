from linebot.models import TextSendMessage


def handle_contact_us() -> TextSendMessage:
    message = (
        "您好 👋 感謝您聯絡我們！\n\n"
        "若您有任何問題或需要協助，歡迎透過以下方式與我們聯繫：\n\n"
        "👤 聯絡人：王大明\n"
        "📱 電話：0912-345-678\n"
        "💬 LINE ID：@yogurtcare"
    )
    return TextSendMessage(text=message)
