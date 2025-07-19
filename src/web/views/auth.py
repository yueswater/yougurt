from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from src.repos.web_member_repo import GoogleSheetWebMemberRepository
from src.utils.password_utils import hash_password

auth_bp = Blueprint("auth", __name__)
repo = GoogleSheetWebMemberRepository()


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        fullname = request.form["fullname"]
        line_id = request.form.get("line_id")  # 取得 Line ID（可為空）

        if repo.exists(username):
            flash("帳號已存在")
        else:
            # 儲存 Web 帳號（假設 repo 支援儲存 line_id）
            repo.add_user(username, hash_password(password), fullname, line_id=line_id)

            # 可選）儲存進 Google Sheet 的 Members 表
            if line_id:
                from datetime import datetime

                from src.repos.member_repo import GoogleSheetMemberRepository

                member_repo = GoogleSheetMemberRepository()
                member_repo.add(
                    {
                        "Line ID": line_id,
                        "Member Name": fullname,
                        "Phone": "",  # 前端可加欄位或保留空白
                        "Create at": datetime.now().isoformat(),
                        "Payment Status": "UNPAID",
                        "Balance": 0,
                        "Valid Member": "FALSE",
                    }
                )

            flash("註冊成功，請登入")
            return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = repo.authenticate(username, password)
        if user:
            session["user"] = {
                "username": user["Username"],
                "fullname": user["Fullname"],
            }
            flash("登入成功")
            return redirect(url_for("home"))
        else:
            flash("帳號或密碼錯誤")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("你已登出")
    return redirect(url_for("home"))
