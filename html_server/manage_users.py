#!/usr/bin/env python3
"""Add or reset an html_server login account.

Run from the html_server/ directory (or anywhere, this script fixes up
sys.path itself):

    python manage_users.py osnat --role user
    python manage_users.py david --role admin

Prompts for the password (not passed as an argv so it doesn't end up in
shell history / process list) and stores a bcrypt hash in data/users.json,
which is gitignored.
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.user_store import set_user_password, user_exists  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage html_server user accounts")
    parser.add_argument("username")
    parser.add_argument("--role", choices=["admin", "user"], default="user")
    args = parser.parse_args()

    if user_exists(args.username):
        print(f"User '{args.username}' already exists; this will reset their password.")

    password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords did not match.", file=sys.stderr)
        sys.exit(1)
    if len(password) < 8:
        print("Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    set_user_password(args.username, password, role=args.role)
    print(f"Saved '{args.username}' with role '{args.role}'.")


if __name__ == "__main__":
    main()
