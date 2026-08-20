import os
from pathlib import Path

# Signs the session cookie. MUST be overridden via env var for any real
# deployment -- the default here is only good enough for local dev, and
# unlike Config/config.toml this value is deliberately NOT meant to be
# checked into git.
SECRET_KEY = os.environ.get("CLINIC_WEB_SECRET_KEY", "dev-insecure-secret-change-me")

SESSION_COOKIE_NAME = "clinic_session"
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60  # 8 hour login session

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

# html_server/app -> html_server -> clinic/ (the repo root Config/config.toml
# and the report letterhead images live in).
REPO_ROOT = APP_DIR.parent.parent

# Anchored to this file's location rather than cwd: html_server must be run
# with the clinic/ repo root as the working directory (Config/config.py and
# Database/dbCreate.py both need that), which is a different directory from
# html_server/ itself, so "app/templates" as a cwd-relative path would break.
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"
