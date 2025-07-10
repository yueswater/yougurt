from flask import Blueprint, render_template, request

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
