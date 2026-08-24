#!/usr/bin/env python3
"""Add, reset, re-role, or delete an html_server login account.

Run from the html_server/ directory (or anywhere, this script fixes up
sys.path itself):

    python manage_users.py osnat --role user       # create, or reset password + role
    python manage_users.py david --role admin       # create, or reset password + role
    python manage_users.py david --set-role user    # change role only, password untouched
    python manage_users.py david --delete           # remove the account

Prompts for the password (not passed as an argv so it doesn't end up in
shell history / process list) and stores a bcrypt hash in data/users.json,
which is gitignored.
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.user_store import delete_user, set_user_password, set_user_role, user_exists  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage html_server user accounts")
    parser.add_argument("username")
    parser.add_argument("--role", choices=["admin", "user"], default="user")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--delete", action="store_true", help="Delete this account")
    mode.add_argument("--set-role", choices=["admin", "user"], help="Change role only, leave password untouched")
    args = parser.parse_args()

    if args.delete:
        if delete_user(args.username):
            print(f"Deleted '{args.username}'.")
        else:
            print(f"User '{args.username}' does not exist.", file=sys.stderr)
            sys.exit(1)
        return

    if args.set_role:
        if set_user_role(args.username, args.set_role):
            print(f"'{args.username}' is now role '{args.set_role}'.")
        else:
            print(f"User '{args.username}' does not exist.", file=sys.stderr)
            sys.exit(1)
        return

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
