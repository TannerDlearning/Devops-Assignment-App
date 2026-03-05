import secrets
import time
from functools import wraps

from flask import session, request, redirect, flash, abort


# -----------------
# CSRF protection
# -----------------

def generate_csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf() -> None:
    """Validate CSRF token for state-changing requests.

    This is a lightweight, tangible implementation (no framework magic), which
    is useful for coursework evidence.
    """
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        expected = session.get("csrf_token")
        if not expected or not sent or sent != expected:
            abort(403)


# -----------------
# Auth / RBAC helpers
# -----------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in to continue.", "error")
            return redirect("/login")
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            flash("Please log in to continue.", "error")
            return redirect("/login")
        if session.get("role") != "admin":
            flash("Access denied: admin privileges required.", "error")
            abort(403)
        return view(*args, **kwargs)

    return wrapped


# -----------------
# Brute-force protection
# -----------------

MAX_ATTEMPTS = 5
LOCK_SECONDS = 5 * 60


def now_unix() -> int:
    return int(time.time())
