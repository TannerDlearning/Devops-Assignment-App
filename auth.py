import sqlite3

from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import db
from security import MAX_ATTEMPTS, LOCK_SECONDS, now_unix

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Basic validation
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if len(username) < 3 or len(username) > 40:
            flash("Username must be 3–40 characters.", "error")
            return render_template("register.html")

        if len(password) < 10:
            flash("Password must be at least 10 characters.", "error")
            return render_template("register.html")

        # SECURITY: store a hashed password
        password_hash = generate_password_hash(password)

        # SECURITY: never allow users to self-assign admin.
        role = "user"

        conn = db.get_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            conn.commit()
            flash("Registered successfully. You can now log in.", "success")
            return redirect("/login")

        except sqlite3.IntegrityError as e:
            # Only show "username exists" if it actually is that constraint
            if "users.username" in str(e):
                flash("Username already exists.", "error")
            else:
                flash(f"Database error: {e}", "error")

        finally:
            conn.close()

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = db.get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        invalid_msg = "Invalid username or password."

        if not user:
            conn.close()
            flash(invalid_msg, "error")
            return render_template("login.html")

        # Brute-force lockout
        lock_until = user["lock_until"]
        if lock_until and int(lock_until) > now_unix():
            remaining = int(lock_until) - now_unix()
            conn.close()
            flash(f"Account locked. Try again in {remaining} seconds.", "error")
            return render_template("login.html")

        stored_hash = user["password_hash"]
        ok = check_password_hash(stored_hash, password)

        if ok:
            # Reset attempts on success
            conn.execute(
                "UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE id = ?",
                (user["id"],),
            )
            conn.commit()
            conn.close()

            session.clear()
            session["user"] = int(user["id"])
            session["role"] = user["role"]
            session.permanent = True
            return redirect("/")

        # Failed login: increment attempts + lock if needed
        attempts = int(user["failed_attempts"] or 0) + 1
        lock_until_val = None
        if attempts >= MAX_ATTEMPTS:
            lock_until_val = now_unix() + LOCK_SECONDS

        conn.execute(
            "UPDATE users SET failed_attempts = ?, lock_until = ? WHERE id = ?",
            (attempts, lock_until_val, user["id"]),
        )
        conn.commit()
        conn.close()

        if lock_until_val:
            flash("Too many failed attempts. Account locked for 5 minutes.", "error")
        else:
            flash(invalid_msg, "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")