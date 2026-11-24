"""Admin-only full-database backup and restore.

Backup downloads the whole database (structure + data) as a plain-text SQL
file; restore replaces the whole database from such a file. The heavy
lifting is in Database/dbBackup.py (Qt-free, so the desktop app can reuse
it); this module adds the safeguards that only make sense for the server:

* admin role required for both;
* restore must carry ?confirm=RESTORE, so a stray request (or a client
  that skipped the two confirmation dialogs) can't wipe the database;
* the file is fully validated before anything is touched;
* a safety backup of the current database is written to
  html_server/data/backups/ immediately before every restore -- on MySQL a
  restore that fails part-way can't be rolled back (DDL commits
  implicitly), so this file is the way back;
* one restore at a time.
"""
import datetime
import threading

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from app.config import DATA_DIR
from app.deps import require_admin_api

from Database.dbBackup import BackupError, dump_database, parse_backup, restore_database

BACKUP_DIR = DATA_DIR / "backups"
KEEP_SAFETY_BACKUPS = 20
CONFIRM_WORD = "RESTORE"

api_router = APIRouter(
    prefix="/api/admin", tags=["admin-api"], dependencies=[Depends(require_admin_api)]
)

_restore_lock = threading.Lock()


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


@api_router.get("/backup")
def download_backup() -> Response:
    try:
        text = dump_database()
    except Exception as e:  # surface DB errors as a readable message
        raise HTTPException(status_code=500, detail=f"Backup failed: {e}") from e
    filename = f"clinic_backup_{_timestamp()}.sql"
    return Response(
        content=text.encode("utf-8"),
        media_type="application/sql; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _write_safety_backup() -> str:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    path = BACKUP_DIR / f"pre_restore_{_timestamp()}.sql"
    path.write_text(dump_database(), encoding="utf-8")
    old = sorted(BACKUP_DIR.glob("pre_restore_*.sql"))[:-KEEP_SAFETY_BACKUPS]
    for p in old:
        p.unlink(missing_ok=True)
    return path.name


def _do_restore(text: str) -> dict:
    if not _restore_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Another restore is already in progress.")
    try:
        try:
            parse_backup(text)  # reject a bad file before anything else happens
        except BackupError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        try:
            safety = _write_safety_backup()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Could not save a safety backup of the current database, so nothing was restored: {e}",
            ) from e
        try:
            result = restore_database(text)
        except BackupError as e:
            raise HTTPException(
                status_code=500,
                detail=f"{e} -- the database as it was just before this restore is saved on the "
                       f"server as html_server/data/backups/{safety}.",
            ) from e
        result["safety_backup"] = safety
        return result
    finally:
        _restore_lock.release()


@api_router.post("/restore")
async def restore(request: Request, confirm: str = Query("")) -> dict:
    if confirm != CONFIRM_WORD:
        raise HTTPException(status_code=400, detail="Restore was not confirmed.")
    raw = await request.body()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="The file is not a UTF-8 text file.")
    return await run_in_threadpool(_do_restore, text)
