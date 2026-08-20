"""Shared Pony ORM session handling.

Reuses the existing Database package (repo root) so html_server and the
PySide6 desktop app read/write the exact same schema and DB -- whichever
one Config/config.toml (or the CLINIC_DB_TYPE env override) points at.
Requires html_server to be run with the clinic/ repo root on sys.path and
as the working directory, same as the desktop app (Config/config.py opens
"./Config/config.toml" relative to cwd).
"""
from pony.orm import db_session

import Database.dbCreate  # noqa: F401  (importing binds the DB via Pony)

__all__ = ["db_session"]
