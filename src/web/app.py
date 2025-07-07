import logging
from datetime import datetime
from uuid import uuid4

import requests
from flask import Blueprint, render_template, request

logging.basicConfig(level=logging.DEBUG)

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def home():
    return render_template("home.html")


@web_bp.route("/register")
def register():
    return render_template("register.html")


@web_bp.route("/login")
def login():
    return render_template("login.html")


@web_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@web_bp.route("/bind")
def bind():
    line_id = request.args.get("line_id")
    name = request.args.get("name")
    phone = request.args.get("phone")

    if not line_id or not name or not phone:
        return render_template("bind_fail.html", message="參數不完整")

    try:
        res = requests.post(
            "http://localhost:8000/api/members/",
            json={
                "member_id": str(uuid4()),
                "member_name": name,
                "line_id": line_id,
                "phone": phone,
                "create_at": datetime.now().isoformat(),
                "order_type": "一般會員",
                "remain_delivery": 0,
                "remain_volume": 0,
                "prepaid": 0,
            },
        )

        logging.debug("狀態碼：", res.status_code)
        logging.debug("錯誤內容：", res.text)
        if res.ok:
            return render_template("bind_success.html", name=name)
        else:
            return render_template("bind_fail.html", message="綁定失敗，請確認是否已註冊過")
    except Exception as e:
        return render_template("bind_fail.html", message=f"伺服器錯誤：{e}")
