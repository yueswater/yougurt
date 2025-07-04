# src/bot/app.py

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
from linebot.models import TextSendMessage
from bot.handlers import user_handler
from dotenv import load_dotenv
import os
import logging

load_dotenv()
app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# 👉 環境變數或硬編碼 Channel Secret / Token
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if user_handler.is_in_binding_process(user_id):
        reply = user_handler.handle_binding_step(user_id, text, line_bot_api)

    elif text == "綁定會員":
        reply = user_handler.initiate_binding(user_id)

    else:
        reply = TextSendMessage(text="請使用圖文選單開始操作，或輸入『綁定會員』")

    line_bot_api.reply_message(event.reply_token, reply)


# src/bot/app.py 最底部加上 👇

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
