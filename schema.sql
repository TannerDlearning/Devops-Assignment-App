DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',

    -- Brute force protection
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    lock_until INTEGER,

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_assets_owner_id ON assets(owner_id);
