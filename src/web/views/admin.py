from datetime import datetime
from uuid import uuid4

from flask import Blueprint, redirect, render_template, request, url_for

from src.models.member import Member
from src.repos.member_repo import GoogleSheetMemberRepository

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/members", methods=["GET"])
def show_members():
    repo = GoogleSheetMemberRepository()
    members = repo.get_all()
    return render_template("admin/members.html", members=members)


@admin_bp.route("/members/confirm", methods=["POST"])
def confirm_payment():
    line_id = request.form.get("line_id")
    repo = GoogleSheetMemberRepository()
    member = repo.get_by_line_id(line_id)
    if member:
        member.valid_member = True
        repo.update(member)
    members = repo.get_all()
    return render_template("admin/members.html", members=members)


@admin_bp.route("/members/partial", methods=["GET"])
def members_partial():
    repo = GoogleSheetMemberRepository()
    members = repo.get_all()
    print("🔥 refreshing partial")
    return render_template("admin/_member_table.html", members=members)


@admin_bp.route("/members/new", methods=["GET"])
def new_member_form():
    return render_template("admin/add_member.html")


@admin_bp.route("/members/create", methods=["POST"])
def create_member():
    form = request.form

    payment_method = form.get("payment_method")  # 現金 or 轉帳
    bank_account = form.get("bank_account") if payment_method == "transfer" else None

    member = Member(
        member_id=uuid4(),
        line_id=form.get("line_id") or None,
        member_name=form.get("member_name"),
        phone=form.get("phone"),
        create_at=datetime.now(),
        order_type=form.get("order_type") or "",
        remain_delivery=int(form.get("remain_delivery") or 0),
        remain_volume=int(form.get("remain_volume") or 0),
        prepaid=int(form.get("prepaid") or 0),
        valid_member=form.get("valid_member") == "true",
        bank_account=bank_account,
    )
    repo = GoogleSheetMemberRepository()
    repo.add(member)
    return redirect(url_for("admin.show_members"))
