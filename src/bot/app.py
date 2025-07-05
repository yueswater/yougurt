# src/bot/app.py

import logging
import os

from dotenv import load_dotenv
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from bot import constants
from bot.handlers import user_handler

load_dotenv()
app = Flask(__name__)

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
    user_id = (
        event.source.user_id
    )  # Line unique ID, e.g., U5bd3d61b7c6235a344238adbe25df5df
    text = event.message.text.strip()
    # If the binding process is in progress
    if user_handler.is_binding_session_active(user_id):
        # If you are already a member, please remind him not to continue tying
        if user_handler.member_service.exists(user_id):
            reply = TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        else:
            reply = user_handler.handle_binding_step(user_id, text, line_bot_api)
    # If you enter "Binding Member"
    elif text == "綁定會員":
        if user_handler.member_service.exists(user_id):
            reply = TextSendMessage(text=constants.Message.get("ALREADY_MEMBER", ""))
        else:
            reply = user_handler.initiate_binding(user_id)

    # Other messages
    else:
        reply = TextSendMessage(text=constants.Message.get("OTHER_NEEDED", ""))
    # Reply to the user
    line_bot_api.reply_message(event.reply_token, reply)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
