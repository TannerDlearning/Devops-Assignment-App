from flask import Blueprint, render_template, request, redirect, flash

import db
from security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/users")
@admin_required
def users():
    conn = db.get_connection()
    users = conn.execute("SELECT id, username, role, created_at FROM users ORDER BY id ASC").fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)


@bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def set_role(user_id: int):
    role = request.form.get("role", "user")
    if role not in {"user", "admin"}:
        flash("Invalid role.", "error")
        return redirect("/admin/users")

    conn = db.get_connection()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()

    flash("User role updated.", "success")
    return redirect("/admin/users")
