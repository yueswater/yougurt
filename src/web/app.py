import logging
import os
from datetime import datetime
from uuid import uuid4

import requests
from dotenv import load_dotenv
from flask import Blueprint, Flask, render_template, request

from flask_session import Session
from src.web.views.liff import liff_bp

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env"))
load_dotenv(dotenv_path)


# Load LINE redirect URI after dotenv
LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI")
print("LINE_REDIRECT_URI =", LINE_REDIRECT_URI)

# Import after env loaded

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ringo123")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
        return render_template("bind_fail.html", message="Missing parameters")

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
                "valid_member": "TRUE",
            },
        )

        logging.debug(f"Status code: {res.status_code}")
        logging.debug(f"Response text: {res.text}")
        if res.ok:
            return render_template("bind_success.html", name=name)
        else:
            return render_template(
                "bind_fail.html", message="Binding failed, maybe already registered"
            )
    except Exception as e:
        return render_template("bind_fail.html", message=f"Server error: {e}")


app.register_blueprint(web_bp)
app.register_blueprint(liff_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)
