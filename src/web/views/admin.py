from datetime import date, datetime, timedelta
from uuid import uuid4

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from src.models.member import Member, PaymentStatus
from src.models.order import DeliverStatus, OrderStatus
from src.repos.member_repo import GoogleSheetMemberRepository
from src.repos.order_repo import GoogleSheetOrderRepository
from src.web.utils.cache import get_cached_members

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ORDER_STATUS_TEXT = {"PENDING": "待確認", "CONFIRMED": "已確認", "CANCELLED": "已取消"}

DELIVER_STATUS_TEXT = {
    "PREPARE": "準備中",
    "DELIVERING": "配送中",
    "DELIVERED": "已送達",
}

# Admin Console


@admin_bp.route("/dashboard")
def dashboard():
    # If not admin user-oriented homepage or give prompts
    if not session.get("user") or session["user"].get("username") != "admin":
        flash("您沒有權限查看此頁面")
        return redirect(url_for("home"))

    return render_template("admin/dashboard.html")


# Member Console


@admin_bp.route("/members", methods=["GET"])
def show_members():
    repo = GoogleSheetMemberRepository()
    members = repo.get_all()
    return render_template("admin/members.html", members=members)


@admin_bp.route("/members/<line_id>/confirm", methods=["POST"])
def confirm_payment(line_id):
    # Check permissions
    if not session.get("user") or session["user"].get("username") != "admin":
        return "權限不足", 403

    print(f"Confirming payment for line_id: {line_id}")

    repo = GoogleSheetMemberRepository()
    member = repo.get_by_line_id(line_id)
    if member:
        member.payment_status = PaymentStatus.PAID
        repo.update(member)
        print("Payment confirmed successfully!")
    else:
        print(f"No member found with line_id: {line_id}")

    members = repo.get_all()
    return render_template("admin/_member_table.html", members=members)


@admin_bp.route("/members/partial", methods=["GET"])
def members_partial():
    search = request.args.get("search", "").strip()
    repo = GoogleSheetMemberRepository()
    if search:
        members = [m for m in repo.get_all() if search in str(m.member_name)]
    else:
        members = repo.get_all()
    return render_template("admin/_member_table.html", members=members)


@admin_bp.route("/members/new", methods=["GET"])
def new_member_form():
    return render_template("admin/add_member.html")


@admin_bp.route("/members/create", methods=["POST"])
def create_member():
    form = request.form

    payment_method = form.get("payment_method")  # Cash or Transfer
    bank_account = form.get("bank_account") if payment_method == "transfer" else None

    # Set payment status according to payment method
    payment_status = (
        PaymentStatus.PAID if payment_method == "cash" else PaymentStatus.UNPAID
    )

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
        remain_free_quota=int(form.get("remain_free_quota") or 0),
        total_delivery_fee=int(form.get("total_delivery_fee") or 0),
        payment_status=payment_status,
    )
    repo = GoogleSheetMemberRepository()
    repo.add(member)
    return redirect(url_for("admin.show_members"))


@admin_bp.route("/members/<line_id>/edit", methods=["GET"])
def edit_member_modal(line_id):
    repo = GoogleSheetMemberRepository()
    member = repo.get_by_line_id(line_id)
    return render_template("admin/_edit_member_modal.html", member=member)


@admin_bp.route("/members/<line_id>/update", methods=["POST"])
def update_member(line_id):
    form = request.form
    repo = GoogleSheetMemberRepository()
    member = repo.get_by_line_id(line_id)

    # Update the column
    member.member_name = form.get("member_name")
    member.phone = form.get("phone")
    member.bank_account = form.get("bank_account") or None
    member.balance = int(form.get("balance") or 0)
    member.remain_delivery = int(form.get("remain_delivery") or 0)

    repo.update(member)
    members = repo.get_all()
    return render_template("admin/members.html", members=members)


@admin_bp.route("/members/<member_id>/freeze", methods=["POST"])
def freeze_member(member_id):
    print(f"🧊 Received member_id from URL: {member_id}")

    repo = GoogleSheetMemberRepository()
    member = repo.get_by_member_id(member_id)  # 注意這裡方法要對應

    if member:
        print(f"🧊 Freezing member: {member.member_name} ({member_id})")
        member.payment_status = PaymentStatus.UNPAID
        repo.update(member)
        print("✅ Member frozen successfully!")
    else:
        print(f"❌ No member found with member_id: {member_id}")

    members = repo.get_all()
    return render_template("admin/_member_table.html", members=members)


# Order Console


@admin_bp.route("/orders", methods=["GET"])
def show_orders():
    search = request.args.get("search", "").strip()
    order_repo = GoogleSheetOrderRepository()
    orders = order_repo.get_all()
    members = get_cached_members()

    # Use dict to quickly check member names
    member_map = {str(m.member_id): m.member_name for m in members}

    for o in orders:
        o.member_name = member_map.get(str(o.member_id), "未知會員")

    if search:
        orders = [o for o in orders if search in str(o.member_name)]

    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/orders/<order_id>/edit", methods=["GET", "POST"])
def edit_order(order_id):
    order_repo = GoogleSheetOrderRepository()
    member_repo = GoogleSheetMemberRepository()

    order = order_repo.get_by_order_id(order_id)
    member = member_repo.get_by_member_id(order.member_id)

    if not order:
        return "找不到訂單", 404

    if request.method == "POST":
        form = request.form
        confirmed_list = form.getlist("confirmed_order")
        confirmed_str = "CONFIRMED" if "CONFIRMED" in confirmed_list else "false"
        order.confirmed_order = (
            OrderStatus.CONFIRMED
            if confirmed_str == "CONFIRMED"
            else OrderStatus.PENDING
        )

        deliver_str = form.get("deliver_status")
        deliver_date_str = form.get("deliver_date")
        order.deliver_status = DeliverStatus[deliver_str] if deliver_str else None
        order.deliver_date = deliver_date_str or None

        order_items_str = form.get("order_items", "").strip()
        if order_items_str:
            parsed_orders = {
                item.split(" * ")[0].strip(): int(item.split(" * ")[1].strip())
                for item in order_items_str.split("、")
                if " * " in item
            }
            order.orders = parsed_orders

        order_repo.update(order)
        return redirect(url_for("admin.show_orders"))

    # GET's logic
    order_items_str = "、".join(
        f"{product_name} * {qty}" for product_name, qty in order.orders.items()
    )

    return render_template(
        "admin/edit_order.html",
        order=order,
        member=member,
        order_items=order_items_str,
        today=date.today(),
        max_date=date.today() + timedelta(days=14),
    )


@admin_bp.route("/orders/<order_id>/delete", methods=["POST"])
def delete_order(order_id):
    repo = GoogleSheetOrderRepository()
    order = repo.get_by_order_id(order_id)

    if not order:
        return "找不到訂單", 404

    repo.delete(order_id)
    return redirect(url_for("admin.show_orders"))
