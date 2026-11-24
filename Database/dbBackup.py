"""Full-database backup/restore as a plain-text SQL dump.

A backup file holds the complete database: the structure (DROP/CREATE
TABLE, plus CREATE INDEX on sqlite) and every row (INSERT statements).
It is ordinary SQL, readable in any text editor, and can also be fed
straight to the `mysql` / `sqlite3` command-line clients by hand.

Like the rest of the Database package this has no Qt dependency, so the
desktop app can reuse it later; html_server's admin routes are the first
caller.

File layout (everything this module needs to validate a file before it
touches the live database):

    -- CLINIC-DB-BACKUP v1
    -- dialect: mysql | sqlite
    -- created: 2026-11-24T10:15:00
    -- tables: patientcore=120, visits=340, ...
    <statements, each ending in ';'>
    -- END OF CLINIC-DB-BACKUP

The footer line is how a truncated (partially downloaded / partially
copied) file is detected: no footer, no restore.

Dialect matters: SHOW CREATE TABLE output from MySQL is not valid sqlite
and vice versa, so a backup can only be restored into the same kind of
database it was taken from.
"""
import datetime
import decimal
import re

from pony.orm import db_session

from Database.dbCreate import db, db_type

MAGIC = "-- CLINIC-DB-BACKUP v1"
FOOTER = "-- END OF CLINIC-DB-BACKUP"

# Multi-row INSERTs: far fewer round trips than one INSERT per row (which
# matters against the MySQL server over the network), while staying well
# under MySQL's default max_allowed_packet (4MB on older servers).
_MAX_INSERT_BYTES = 512 * 1024


class BackupError(Exception):
    """A backup file was rejected, or the restore itself failed."""


# ---------------------------------------------------------------------------
# Value / identifier quoting
# ---------------------------------------------------------------------------

def _quote_ident(name: str) -> str:
    if db_type == "mysql":
        return "`" + name.replace("`", "``") + "`"
    return '"' + name.replace('"', '""') + '"'


def _quote_str(s: str) -> str:
    if db_type == "mysql":
        # Default MySQL sql_mode treats backslash as an escape character.
        s = (s.replace("\\", "\\\\").replace("'", "\\'")
              .replace("\0", "\\0").replace("\x1a", "\\Z"))
        return "'" + s + "'"
    return "'" + s.replace("'", "''") + "'"


def _literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, decimal.Decimal)):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return _quote_str(value.isoformat(sep=" ") if isinstance(value, datetime.datetime)
                          else value.isoformat())
    if isinstance(value, datetime.timedelta):
        # pymysql returns MySQL TIME columns as timedelta.
        us = (value.days * 86400 + value.seconds) * 1_000_000 + value.microseconds
        sign = "-" if us < 0 else ""
        secs, micro = divmod(abs(us), 1_000_000)
        h, rem = divmod(secs, 3600)
        m, sec = divmod(rem, 60)
        frac = f".{micro:06d}" if micro else ""
        return _quote_str(f"{sign}{h:02d}:{m:02d}:{sec:02d}{frac}")
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "X'" + bytes(value).hex() + "'"
    return _quote_str(str(value))


# ---------------------------------------------------------------------------
# Introspection of the live database
# ---------------------------------------------------------------------------

def _list_tables(cursor) -> list[str]:
    if db_type == "mysql":
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        return [r[0] for r in cursor.fetchall()]
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    return [r[0] for r in cursor.fetchall()]


def _parent_tables(cursor, table: str) -> set[str]:
    if db_type == "mysql":
        cursor.execute(
            "SELECT DISTINCT REFERENCED_TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s "
            "AND REFERENCED_TABLE_NAME IS NOT NULL",
            (table,),
        )
    else:
        cursor.execute(f"PRAGMA foreign_key_list({_quote_ident(table)})")
        return {r[2] for r in cursor.fetchall()} - {table}
    return {r[0] for r in cursor.fetchall()} - {table}


def _dependency_order(cursor, tables: list[str]) -> list[str]:
    """Parents before children, so creates/inserts never violate a foreign
    key. Needed on sqlite in particular: Pony turns foreign_keys on for
    every connection and the pragma can't be switched off mid-transaction.
    """
    parents = {t: _parent_tables(cursor, t) & set(tables) for t in tables}
    ordered: list[str] = []
    remaining = sorted(tables)
    while remaining:
        ready = [t for t in remaining if parents[t] <= set(ordered)]
        if not ready:  # a cycle -- shouldn't happen with this schema
            ready = remaining[:1]
        ordered.extend(ready)
        remaining = [t for t in remaining if t not in ready]
    return ordered


def _create_statements(cursor, table: str) -> list[str]:
    if db_type == "mysql":
        cursor.execute(f"SHOW CREATE TABLE {_quote_ident(table)}")
        return [cursor.fetchone()[1]]
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE tbl_name = ? AND sql IS NOT NULL "
        "ORDER BY CASE type WHEN 'table' THEN 0 ELSE 1 END, name",
        (table,),
    )
    return [r[0] for r in cursor.fetchall()]


def _expected_tables() -> set[str]:
    return {e._table_.lower() if isinstance(e._table_, str) else str(e._table_).lower()
            for e in db.entities.values()}


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

def dump_database() -> str:
    """Return the complete database (structure + data) as SQL text."""
    with db_session:
        cursor = db.get_connection().cursor()
        tables = _dependency_order(cursor, _list_tables(cursor))

        body: list[str] = []
        counts: list[str] = []

        if db_type == "mysql":
            body.append("SET FOREIGN_KEY_CHECKS = 0;")

        # Drop children before parents.
        for table in reversed(tables):
            body.append(f"DROP TABLE IF EXISTS {_quote_ident(table)};")

        for table in tables:
            body.append("")
            body.append(f"-- Table: {table}")
            for stmt in _create_statements(cursor, table):
                body.append(stmt.rstrip().rstrip(";") + ";")

            cursor.execute(f"SELECT * FROM {_quote_ident(table)}")
            columns = ", ".join(_quote_ident(d[0]) for d in cursor.description)
            prefix = f"INSERT INTO {_quote_ident(table)} ({columns}) VALUES\n"
            rows = cursor.fetchall()
            counts.append(f"{table}={len(rows)}")

            batch: list[str] = []
            size = 0
            for row in rows:
                tup = "(" + ", ".join(_literal(v) for v in row) + ")"
                if batch and size + len(tup) > _MAX_INSERT_BYTES:
                    body.append(prefix + ",\n".join(batch) + ";")
                    batch, size = [], 0
                batch.append(tup)
                size += len(tup) + 2
            if batch:
                body.append(prefix + ",\n".join(batch) + ";")

        if db_type == "mysql":
            body.append("")
            body.append("SET FOREIGN_KEY_CHECKS = 1;")

    header = [
        MAGIC,
        f"-- dialect: {db_type}",
        f"-- created: {datetime.datetime.now().isoformat(timespec='seconds')}",
        f"-- tables: {', '.join(counts)}",
        "",
    ]
    return "\n".join(header + body + ["", FOOTER, ""])


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

def _split_statements(text: str) -> list[str]:
    """Split SQL text on ';' that sit outside quoted strings/identifiers,
    dropping '--' comment lines. Patient text can contain ';', quotes and
    newlines, so a naive split would corrupt data."""
    statements: list[str] = []
    buf: list[str] = []
    quote = None
    i, n = 0, len(text)
    backslash_escapes = db_type == "mysql"
    while i < n:
        c = text[i]
        if quote:
            buf.append(c)
            if backslash_escapes and quote == "'" and c == "\\" and i + 1 < n:
                buf.append(text[i + 1])
                i += 2
                continue
            if c == quote:
                if i + 1 < n and text[i + 1] == quote:  # doubled quote escape
                    buf.append(text[i + 1])
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if c in ("'", '"', "`"):
            quote = c
            buf.append(c)
        elif c == "-" and text.startswith("--", i):
            nl = text.find("\n", i)
            i = n if nl == -1 else nl
            continue
        elif c == ";":
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
        else:
            buf.append(c)
        i += 1
    if quote:
        raise BackupError("The file ends inside a quoted value; it looks truncated or corrupted.")
    if "".join(buf).strip():
        raise BackupError("The file ends with an incomplete SQL statement.")
    return statements


_IDENT = r'(?:`(?:[^`]|``)+`|"(?:[^"]|"")+"|\w+)'
_ALLOWED = [
    re.compile(rf"^DROP TABLE IF EXISTS ({_IDENT})$", re.I | re.S),
    re.compile(rf"^CREATE TABLE ({_IDENT})\s*\(", re.I | re.S),
    re.compile(rf"^CREATE (?:UNIQUE )?INDEX {_IDENT} ON ({_IDENT})\s*\(", re.I | re.S),
    re.compile(rf"^INSERT INTO ({_IDENT})\s*\(", re.I | re.S),
    re.compile(r"^SET FOREIGN_KEY_CHECKS = [01]$", re.I),
]


def _unquote(ident: str) -> str:
    if ident[0] in "`\"" and ident[-1] == ident[0]:
        return ident[1:-1].replace(ident[0] * 2, ident[0])
    return ident


def parse_backup(text: str) -> dict:
    """Validate a backup file without touching the database. Returns
    {"created", "dialect", "tables", "statements"}; raises BackupError."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != MAGIC:
        raise BackupError("This is not a clinic database backup file (missing header).")
    if text.rstrip().splitlines()[-1].strip() != FOOTER:
        raise BackupError("The backup file is incomplete (missing end marker). It may have been truncated.")

    meta = {}
    for line in lines[1:6]:
        m = re.match(r"^-- (\w+): (.*)$", line.strip())
        if m:
            meta[m.group(1)] = m.group(2)

    dialect = meta.get("dialect")
    if dialect != db_type:
        raise BackupError(
            f"This backup was taken from a {dialect or 'unknown'} database, but the server "
            f"is using {db_type}. It can only be restored into the same kind of database."
        )

    statements = _split_statements(text)
    created_tables: set[str] = set()
    for stmt in statements:
        for pattern in _ALLOWED:
            m = pattern.match(stmt)
            if m:
                if stmt[:12].upper().startswith("CREATE TABLE"):
                    created_tables.add(_unquote(m.group(1)).lower())
                break
        else:
            raise BackupError(f"Unexpected statement in backup file: {stmt[:80]!r}")

    missing = _expected_tables() - created_tables
    if missing:
        raise BackupError(
            "The backup file is missing tables the application needs: " + ", ".join(sorted(missing))
        )

    tables = {}
    for part in meta.get("tables", "").split(","):
        if "=" in part:
            name, _, count = part.strip().partition("=")
            tables[name] = int(count) if count.isdigit() else count

    return {"created": meta.get("created"), "dialect": dialect,
            "tables": tables, "statements": statements}


def restore_database(text: str) -> dict:
    """Replace the entire database with the contents of a backup file.

    On sqlite the whole restore runs in one transaction: any failure rolls
    back to exactly the previous state. On MySQL, DROP/CREATE TABLE commit
    implicitly, so a failure part-way can leave the database partially
    restored -- callers should take a safety backup first (html_server does).

    Returns the row count of each table after the restore.
    """
    parsed = parse_backup(text)
    try:
        with db_session:
            cursor = db.get_connection().cursor()
            try:
                for stmt in parsed["statements"]:
                    cursor.execute(stmt)
            finally:
                if db_type == "mysql":
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            db.commit()

        with db_session:
            cursor = db.get_connection().cursor()
            counts = {}
            for table in _list_tables(cursor):
                cursor.execute(f"SELECT COUNT(*) FROM {_quote_ident(table)}")
                counts[table] = cursor.fetchone()[0]
    except BackupError:
        raise
    except Exception as e:
        raise BackupError(f"Restore failed: {e}") from e

    return {"created": parsed["created"], "tables": counts}
