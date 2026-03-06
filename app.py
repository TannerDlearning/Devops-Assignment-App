import os
import secrets
from datetime import timedelta

from flask import Flask, session, g

import db
import auth
import assets
import admin
from security import generate_csrf_token, validate_csrf


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    A factory pattern makes the app easier to test (pytest) and deploy.
    """

    app = Flask(__name__)

    app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )

    if test_config:
        app.config.update(test_config)

    db.init_db()

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf_token}

    @app.before_request
    def csrf_protect():
        validate_csrf()

    app.register_blueprint(auth.bp)
    app.register_blueprint(assets.bp)
    app.register_blueprint(admin.bp)

    @app.before_request
    def load_logged_in_user():
        g.user = session.get("user")
        g.role = session.get("role")

    @app.errorhandler(403)
    def forbidden(_e):
        return "Forbidden", 403

    @app.errorhandler(404)
    def not_found(_e):
        return "Not found", 404

    return app


app = create_app()


if __name__ == "__main__":
    db.init_db()
    app.run(debug=False)
