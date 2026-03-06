import os
import sqlite3
from flask import current_app


def _db_path() -> str:
    try:
        cfg = current_app.config
        if cfg.get("DATABASE"):
            return str(cfg["DATABASE"])
    except RuntimeError:
        pass

    return os.environ.get("DATABASE_PATH", "data.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def init_db() -> None:
    """Create database and apply simple migrations if needed."""

    path = os.environ.get("DATABASE_PATH", "data.db")
    first_time = not os.path.exists(path)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    if first_time:
        with open("schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        return

    table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone()

    if table_exists:
        cols = _table_columns(conn, "users")

        if "password_hash" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

        if "failed_attempts" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")

        if "lock_until" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN lock_until INTEGER")

        if "created_at" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
            conn.execute(
                "UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL"
            )

    conn.commit()
    conn.close()