from flask import Blueprint, render_template, request, redirect, session, flash, abort

import db
from security import login_required, admin_required

bp = Blueprint("assets", __name__)

ALLOWED_TYPES = {"Laptop", "Desktop", "Monitor", "Phone", "Tablet", "Other"}


def _validate_asset(name: str, type_: str) -> tuple[bool, str]:
    if not name or len(name) > 80:
        return False, "Asset name is required (max 80 characters)."
    if type_ not in ALLOWED_TYPES:
        return False, f"Asset type must be one of: {', '.join(sorted(ALLOWED_TYPES))}."
    return True, ""


@bp.route("/")
@login_required
def dashboard():
    conn = db.get_connection()
    assets = conn.execute(
        """
        SELECT assets.id, assets.name, assets.type, users.username, assets.owner_id
        FROM assets
        JOIN users ON assets.owner_id = users.id
        ORDER BY assets.id DESC
        """
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", assets=assets)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_asset():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        type_ = request.form.get("type", "Other").strip()

        ok, msg = _validate_asset(name, type_)
        if not ok:
            flash(msg, "error")
            return render_template("asset_form.html", asset=None, allowed_types=sorted(ALLOWED_TYPES))

        conn = db.get_connection()
        conn.execute(
            "INSERT INTO assets (name, type, owner_id) VALUES (?, ?, ?)",
            (name, type_, session["user"]),
        )
        conn.commit()
        conn.close()
        flash("Asset created.", "success")
        return redirect("/")

    return render_template("asset_form.html", asset=None, allowed_types=sorted(ALLOWED_TYPES))


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_asset(id: int):
    conn = db.get_connection()
    asset = conn.execute("SELECT * FROM assets WHERE id = ?", (id,)).fetchone()

    if not asset:
        conn.close()
        abort(404)

    if int(asset["owner_id"]) != int(session["user"]):
        conn.close()
        abort(403)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        type_ = request.form.get("type", "Other").strip()

        ok, msg = _validate_asset(name, type_)
        if not ok:
            conn.close()
            flash(msg, "error")
            return render_template("asset_form.html", asset=asset, allowed_types=sorted(ALLOWED_TYPES))

        conn.execute("UPDATE assets SET name = ?, type = ? WHERE id = ?", (name, type_, id))
        conn.commit()
        conn.close()
        flash("Asset updated.", "success")
        return redirect("/")

    conn.close()
    return render_template("asset_form.html", asset=asset, allowed_types=sorted(ALLOWED_TYPES))


@bp.route("/delete/<int:id>", methods=["POST"])
@admin_required
def delete_asset(id: int):
    conn = db.get_connection()
    conn.execute("DELETE FROM assets WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Asset deleted.", "success")
    return redirect("/")
