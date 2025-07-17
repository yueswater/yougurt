from datetime import datetime
from uuid import uuid4

from flask import Blueprint, redirect, render_template, request, url_for

from src.models.member import Member
from src.models.order import DeliverStatus, OrderStatus
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.web.utils.cache import get_cached_members

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ORDER_STATUS_TEXT = {"PENDING": "待確認", "CONFIRMED": "已確認", "CANCELLED": "已取消"}

DELIVER_STATUS_TEXT = {"PREPARE": "準備中", "DELIVERING": "配送中", "DELIVERED": "已送達"}


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

    payment_method = form.get("payment_method")  # Cash or Transfer
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
        balance=int(form.get("balance") or 0),
        valid_member=form.get("valid_member") == "true",
        bank_account=bank_account,
    )
    repo = GoogleSheetMemberRepository()
    repo.add(member)
    return redirect(url_for("admin.show_members"))


@admin_bp.route("/orders", methods=["GET"])
def show_orders():
    order_repo = GoogleSheetOrderRepository()
    GoogleSheetMemberRepository()

    orders = order_repo.get_all()
    members = get_cached_members()

    # Use dict to quickly check member names
    member_map = {str(m.member_id): m.member_name for m in members}

    for o in orders:
        # # 狀態中文
        # o.confirmed_order_text = ORDER_STATUS_TEXT.get(
        #     o.confirmed_order.name
        #     if hasattr(o.confirmed_order, "name")
        #     else str(o.confirmed_order),
        #     str(o.confirmed_order),
        # )
        # o.deliver_status_text = DELIVER_STATUS_TEXT.get(
        #     o.deliver_status.name
        #     if hasattr(o.deliver_status, "name")
        #     else str(o.deliver_status),
        #     str(o.deliver_status),
        # )

        # Add member name
        o.member_name = member_map.get(str(o.member_id), "未知會員")

    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/orders/<order_id>/edit", methods=["GET"])
def edit_order(order_id):
    repo = GoogleSheetOrderRepository()
    order = repo.get_by_order_id(order_id)
    if not order:
        return "找不到訂單", 404
    return render_template("admin/edit_order.html", order=order)


@admin_bp.route("/orders/<order_id>/edit", methods=["POST"])
def update_order(order_id):
    repo = GoogleSheetOrderRepository()
    order = repo.get_by_order_id(order_id)
    if not order:
        return "找不到訂單", 404

    form = request.form

    # Fix checkbox transmission logic
    confirmed_list = form.getlist("confirmed_order")
    confirmed_str = "CONFIRMED" if "CONFIRMED" in confirmed_list else "false"
    order.confirmed_order = (
        OrderStatus.CONFIRMED if confirmed_str == "CONFIRMED" else OrderStatus.PENDING
    )

    # Shipping status and date
    deliver_str = form.get("deliver_status")
    deliver_date_str = form.get("deliver_date")
    order.deliver_status = DeliverStatus[deliver_str] if deliver_str else None
    order.deliver_date = deliver_date_str or None

    repo.update(order)
    return redirect(url_for("admin.show_orders"))
