import os
import tempfile

import pytest

from app import create_app


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    test_app = create_app({"TESTING": True, "DATABASE": db_path, "SECRET_KEY": "test"})
    import sqlite3

    conn = sqlite3.connect(db_path)
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    from werkzeug.security import generate_password_hash

    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        ("admin", generate_password_hash("AdminPassword123"), "admin"),
    )
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        ("user", generate_password_hash("UserPassword123"), "user"),
    )
    conn.commit()
    conn.close()

    yield test_app

    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username: str, password: str):
    client.get("/login")
    with client.session_transaction() as sess:
        token = sess.get("csrf_token")
    return client.post(
        "/login",
        data={"username": username, "password": password, "csrf_token": token},
        follow_redirects=False,
    )
