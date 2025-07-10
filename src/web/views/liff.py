import os

import requests

# 載入 .env（確保在 app.py 裡也有 load_dotenv）
from dotenv import load_dotenv
from flask import Blueprint, redirect, render_template, request

load_dotenv()

liff_bp = Blueprint("liff", __name__)

# 設定參數
LINE_LOGIN_CHANNEL_ID = os.getenv("LINE_LOGIN_CHANNEL_ID")
LINE_LOGIN_CHANNEL_SECRET = os.getenv("LINE_LOGIN_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI")

# Debug 用，確認實際使用的 redirect URI
print("==> LINE_LOGIN_CHANNEL_ID =", LINE_LOGIN_CHANNEL_ID)
print("==> LINE_REDIRECT_URI =", LINE_REDIRECT_URI)


@liff_bp.route("/liff/login")
def liff_login():
    url = (
        "https://access.line.me/oauth2/v2.1/authorize"
        "?response_type=code"
        f"&client_id={LINE_LOGIN_CHANNEL_ID}"
        f"&redirect_uri={LINE_REDIRECT_URI}"
        "&state=12345"
        "&scope=openid%20profile"
    )
    return redirect(url)


@liff_bp.route("/liff/login/callback")
def liff_login_callback():
    code = request.args.get("code")
    if not code:
        return "缺少 code", 400

    # Step 1: 拿 token
    token_res = requests.post(
        "https://api.line.me/oauth2/v2.1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINE_REDIRECT_URI,
            "client_id": LINE_LOGIN_CHANNEL_ID,
            "client_secret": LINE_LOGIN_CHANNEL_SECRET,
        },
    )

    if not token_res.ok:
        return f"Token 交換失敗：{token_res.text}", 400

    access_token = token_res.json().get("access_token")

    # Step 2: 拿 user profile
    profile_res = requests.get(
        "https://api.line.me/v2/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if not profile_res.ok:
        return f"取得使用者資料失敗：{profile_res.text}", 400

    profile = profile_res.json()
    user_id = profile.get("userId")
    display_name = profile.get("displayName")

    # Step 3: redirect 到 /liff/bind 頁面（由你自行綁定用戶）
    return redirect(f"/liff/bind?line_id={user_id}&display_name={display_name}")


@liff_bp.route("/liff/bind")
def liff_bind():
    line_id = request.args.get("line_id")
    display_name = request.args.get("display_name")
    return render_template("liff/bind.html", line_id=line_id, display_name=display_name)
