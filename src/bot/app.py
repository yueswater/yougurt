import logging
import os

from dotenv import load_dotenv
from flask import request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, PostbackEvent, TextMessage

from src.bot.handlers import handler_router, order_handler
from src.core.session.order_session_store import OrderSessionStore

# 初始化 session store（如已初始化可刪除）
order_session = OrderSessionStore()

load_dotenv()

# TODO: extract to be logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Secret token
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# Initialize Line Bot & handler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


def register_linebot(app):
    @app.route("/callback", methods=["POST"])
    def callback():
        """
        Verify signature when connecting to Line service.
        """
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

        reply = handler_router.dispatch(user_id, text, line_bot_api)
        line_bot_api.reply_message(event.reply_token, reply)

    @handler.add(PostbackEvent)
    def handle_postback(event):
        user_id = event.source.user_id
        data = event.postback.data
        params = event.postback.params

        # 特殊處理：日期選擇
        if "action=select_date" in data and params:
            selected_date = params.get("date")
            reply = order_handler.handle_selected_date(user_id, selected_date)
        else:
            # 一般 postback 處理
            reply = handler_router.dispatch_postback(user_id, data, line_bot_api)

        line_bot_api.reply_message(event.reply_token, reply)
