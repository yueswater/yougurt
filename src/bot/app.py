# src/bot/app.py

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
from linebot.models import TextSendMessage

from bot.handlers.user_handler import bind_user_profile

import os

app = Flask(__name__)

# 👉 環境變數或硬編碼 Channel Secret / Token
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "bvCf8poDf9DXhnCBmgkFLI4+oZOsW6NE3YW/53qrdWOeahnibXUl97hJduXO6nRF34h1w8E93Rkn7QzKK6lJl5wPWSklhe37jo8ChF33DqGk4/7pC7I+NmQZLQvcMWoOzRTuJCI/OPAyzFxzh4EOnAdB04t89/1O/w1cDnyilFU=")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "07dc19f50d60d99784b37ec2e92ce93a")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# # 💬 處理文字訊息
# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     text = event.message.text.strip()
#     if text == "綁定會員":
#         reply = bind_user_profile(event, line_bot_api)
#         line_bot_api.reply_message(event.reply_token, reply)

# src/bot/app.py

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    print(f"收到來自 {user_id} 的訊息：{text}")

    # 測試回覆
    reply = TextSendMessage(text="我收到了你的訊息 ✅")
    line_bot_api.reply_message(event.reply_token, reply)

# src/bot/app.py 最底部加上 👇

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
