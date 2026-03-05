import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import argparse
import db
from werkzeug.security import generate_password_hash

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    conn = db.get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
        (args.username, generate_password_hash(args.password))
    )
    conn.commit()
    conn.close()
    print("Admin user created.")


if __name__ == "__main__":
    main()
