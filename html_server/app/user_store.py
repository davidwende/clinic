"""Minimal JSON-backed user store for html_server logins.

Replaces the desktop app's unsalted-SHA256 / hardcoded-username scheme
(Config/config.toml + Application_Login/Login.py) with bcrypt-hashed
passwords and an explicit role field, so "is this user an admin" is no
longer a literal username check.

Not wired to any admin UI on purpose -- accounts are managed with
manage_users.py from the command line. data/users.json is gitignored.
"""
import json
from typing import Optional, TypedDict

from app.config import DATA_DIR, USERS_FILE
from app.security import hash_password, verify_password


class UserRecord(TypedDict):
    password_hash: str
    role: str  # "admin" or "user"


def _load() -> dict[str, UserRecord]:
    if not USERS_FILE.exists():
        return {}
    return json.loads(USERS_FILE.read_text())


def _save(users: dict[str, UserRecord]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))


def user_exists(username: str) -> bool:
    return username in _load()


def set_user_password(username: str, password: str, role: str = "user") -> None:
    users = _load()
    users[username] = {"password_hash": hash_password(password), "role": role}
    _save(users)


def delete_user(username: str) -> bool:
    users = _load()
    if username not in users:
        return False
    del users[username]
    _save(users)
    return True


def verify_user(username: str, password: str) -> Optional[dict]:
    """Returns {"username": ..., "role": ...} on success, else None."""
    record = _load().get(username)
    if not record or not verify_password(password, record["password_hash"]):
        return None
    return {"username": username, "role": record.get("role", "user")}
