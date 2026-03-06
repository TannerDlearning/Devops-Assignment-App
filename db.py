import os
import sqlite3
import shutil
from flask import current_app


def _default_db_path() -> str:
    if os.environ.get("VERCEL"):
        return "/tmp/data.db"
    return "data.db"


def _db_path() -> str:
    try:
        cfg = current_app.config
        if cfg.get("DATABASE"):
            return str(cfg["DATABASE"])
    except RuntimeError:
        pass

    return os.environ.get("DATABASE_PATH", _default_db_path())


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def init_db(path: str | None = None) -> None:
    path = path or _db_path()
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    source_db = "data.db"

    if (
        os.environ.get("VERCEL")
        and not os.path.exists(path)
        and os.path.exists(source_db)
        and os.path.abspath(source_db) != os.path.abspath(path)
    ):
        shutil.copyfile(source_db, path)

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