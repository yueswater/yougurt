from flask import Blueprint, render_template

from src.repos.member_repo import GoogleSheetMemberRepository

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/members", methods=["GET"])
def show_members():
    repo = GoogleSheetMemberRepository()
    members = repo.get_all()
    return render_template("admin/members.html", members=members)
