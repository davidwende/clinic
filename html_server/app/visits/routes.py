import datetime
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import REPO_ROOT, TEMPLATES_DIR
from app.db import db_session
from pony.orm import IntegrityError, InterfaceError, OperationalError, commit
from app.deps import require_login_api, require_login_page
from app.schemas import VisitDatesOut, VisitIn, VisitOut
from app.visits.field_lists import GROUPED_FIELDS, STR_FIELDS

from Config.config import header as report_header
from Config.config import tail as report_tail
from Database.dbCreate import PatientCore
from Database.dbFuncs import (
    delete_visit,
    get_all_diagnoses,
    get_all_procedures,
    get_visit,
    get_visit_dates,
    patient_exists,
    save_visit,
    visit_exists,
)
from Reports.reports import Report

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

page_router = APIRouter(tags=["visits-page"])
api_router = APIRouter(prefix="/api", tags=["visits-api"], dependencies=[Depends(require_login_api)])


def _require_patient(tz: str) -> None:
    if not patient_exists(tz):
        raise HTTPException(404, "Patient not found")


# Config/config.toml's report header/tail (shared with the desktop app --
# see Report generation below) hardcode these two images as file:// URLs,
# which the Qt app's native renderer can open directly but a real browser
# refuses to load from an http(s) page for security reasons, regardless of
# whether it's the same machine. Rather than rewrite config.toml (which
# would break the desktop app's own rendering), the web report gets these
# same two images re-served over plain HTTP and swaps the URLs in its own
# copy of the HTML -- config.toml and Reports/reports.py are untouched.
REPORT_IMAGES = {"logo_small.png", "signature_stamp.png"}


def _report_filename_stem(tz: str, visit_date: datetime.date) -> str:
    """e.g. tz=123456789, visit_date=2026-08-20 -> "123456789_20260820".

    Deliberately not the same as Visits/visits.py's print_summary(), which
    names its saved-to-file report f"{tz}_{visit_date}.html" -- str(date)
    includes dashes ("2026-08-20"). This compact YYYYMMDD form is a web-app
    convention requested separately from matching the Qt app's naming.
    """
    return f"{tz}_{visit_date.strftime('%Y%m%d')}"


@page_router.get("/report-assets/{filename}")
def report_asset(filename: str):
    if filename not in REPORT_IMAGES:
        raise HTTPException(404)
    path = REPO_ROOT / filename
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


# ---------------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------------

@page_router.get("/patients/{tz}/visits")
def visits_page(tz: str, request: Request, user: dict = Depends(require_login_page)):
    with db_session:
        p = PatientCore.get(tz=tz)
        if not p:
            raise HTTPException(404, "Patient not found")
        context = {"user": user, "tz": tz, "fname": p.fname, "surname": p.surname}
    return templates.TemplateResponse(request, "visits.html", context)


# ---------------------------------------------------------------------------
# JSON API -- mirrors Visits/visits.py's VisitForm
# ---------------------------------------------------------------------------

def _visit_out(v, procs, diags, visit_date: datetime.date, *, is_new: bool) -> VisitOut:
    data = {}
    for fields in GROUPED_FIELDS.values():
        for name in fields:
            raw = getattr(v, name)
            data[name] = (raw or "") if name in STR_FIELDS else bool(raw)
    data["examination"] = v.examination or ""
    data["tests"] = v.tests or ""
    data["recommendation"] = v.recommendation or ""
    data["procedures"] = dict(procs)
    data["diagnoses"] = dict(diags)
    return VisitOut(visit_date=visit_date, is_new=is_new, **data)


def _blank_visit_out(visit_date: datetime.date) -> VisitOut:
    kwargs = {}
    for fields in GROUPED_FIELDS.values():
        for name in fields:
            kwargs[name] = "" if name in STR_FIELDS else False
    kwargs["hip_pelvic_tilt_type"] = "Normal"
    kwargs["examination"] = ""
    kwargs["tests"] = ""
    kwargs["recommendation"] = ""
    kwargs["procedures"] = {}
    kwargs["diagnoses"] = {}
    return VisitOut(visit_date=visit_date, is_new=True, **kwargs)


def _group_tuple(body: VisitIn, fields: list[str]) -> tuple:
    return tuple(getattr(body, f) for f in fields)


@api_router.get("/patients/{tz}/visits/dates", response_model=VisitDatesOut)
def list_visit_dates(tz: str):
    with db_session:
        _require_patient(tz)
        existing = list(get_visit_dates(tz))
    today = datetime.date.today()
    dates = list(existing)
    if not dates or dates[-1] != today:
        dates.append(today)
    return VisitDatesOut(dates=dates, today=today)


@api_router.get("/patients/{tz}/visits/{visit_date}", response_model=VisitOut)
def get_visit_route(tz: str, visit_date: datetime.date):
    with db_session:
        _require_patient(tz)
        if not visit_exists(tz, visit_date):
            return _blank_visit_out(visit_date)
        v, procs, diags = get_visit(tz, visit_date)
        return _visit_out(v, procs, diags, visit_date, is_new=False)


# Pony's own wording for an over-long string column, e.g.
#   "Value for attribute Visits.cc_onset is too long. Max length is 100, value length is 150"
_TOO_LONG_RE = re.compile(
    r"Value for attribute (\w+)\.(\w+) is too long\. Max length is (\d+), value length is (\d+)"
)

NOT_SAVED = "The visit was NOT saved."


def _save_error(status: int, reason: str, message: str, field: str | None = None) -> HTTPException:
    # Structured detail so the client can say *why* and point at the field;
    # visits.js also still copes with a plain-string detail (404s, etc.).
    return HTTPException(status, {"reason": reason, "message": message, "field": field})


def _exception_chain(err: BaseException):
    seen = set()
    stack = [err]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen:
            continue
        seen.add(id(e))
        yield e
        # Pony's CommitException keeps the real causes as sys.exc_info() tuples.
        for item in getattr(e, "exceptions", None) or []:
            stack.append(item[1] if isinstance(item, tuple) else item)
        stack.append(e.__cause__)
        stack.append(e.__context__)


def _describe_save_failure(err: BaseException) -> HTTPException:
    """Turn whatever save_visit()/commit() raised into a message a clinician can act on."""
    chain = list(_exception_chain(err))
    for e in chain:
        m = _TOO_LONG_RE.search(str(e))
        if m:
            entity, attr, max_len, actual = m.groups()
            if entity in ("Procedures", "Diagnoses"):
                kind = "procedure" if entity == "Procedures" else "diagnosis"
                return _save_error(
                    422, "too_long",
                    f"A {kind} name is too long ({actual} characters; the maximum is {max_len}). "
                    f"Shorten it in the {entity} section and save again. {NOT_SAVED}",
                    field=entity.lower(),
                )
            return _save_error(
                422, "too_long",
                f"Text is too long ({actual} characters; the maximum is {max_len}). "
                f"Shorten it and save again. {NOT_SAVED}",
                field=attr,
            )
    for e in chain:
        if isinstance(e, (OperationalError, InterfaceError)):
            return _save_error(
                503, "db_unavailable",
                f"The database server could not be reached or dropped the connection ({e}). "
                f"{NOT_SAVED} Check the network connection to the database server, then save again "
                f"-- your entries are still on screen.",
            )
    for e in chain:
        if isinstance(e, IntegrityError):
            return _save_error(
                409, "integrity",
                f"The database rejected the data as inconsistent ({e}). {NOT_SAVED}",
            )
    return _save_error(
        500, "unexpected",
        f"Unexpected error while saving ({type(err).__name__}: {err}). {NOT_SAVED}",
    )


@api_router.put("/patients/{tz}/visits/{visit_date}", response_model=VisitOut)
def save_visit_route(tz: str, visit_date: datetime.date, body: VisitIn):
    today = datetime.date.today()
    if visit_date != today:
        raise _save_error(
            400, "not_today",
            f"Only today's visit can be saved. This visit is dated {visit_date}, but today is {today} "
            f"(if the page was left open past midnight, reload it). {NOT_SAVED}",
        )

    cc = _group_tuple(body, GROUPED_FIELDS["cc"])
    loc = _group_tuple(body, GROUPED_FIELDS["loc"])
    back = _group_tuple(body, GROUPED_FIELDS["back"])
    hip = _group_tuple(body, GROUPED_FIELDS["hip"])
    neck = _group_tuple(body, GROUPED_FIELDS["neck"])
    shoulder = _group_tuple(body, GROUPED_FIELDS["shoulder"])
    knee = _group_tuple(body, GROUPED_FIELDS["knee"])
    ankle = _group_tuple(body, GROUPED_FIELDS["ankle"])
    anklest = _group_tuple(body, GROUPED_FIELDS["anklest"])
    exam = [body.examination]
    tests = [body.tests]
    recommend = [body.recommendation]

    # Commit explicitly inside the try: left to the implicit commit at the end
    # of `with db_session`, a failure there escaped as a bare 500 with no
    # explanation.
    try:
        with db_session:
            _require_patient(tz)
            ret = save_visit(
                tz, visit_date, cc, loc, back, knee, ankle, anklest,
                hip, neck, shoulder, exam, tests, body.procedures, body.diagnoses, recommend,
            )
            if ret != 0:  # error_codes.ERR_OK
                raise _save_error(
                    500, "save_failed",
                    f"The database layer could not create or open this visit record "
                    f"(see the server log for details). {NOT_SAVED}",
                )
            commit()
    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Saving visit %s/%s failed", tz, visit_date)
        raise _describe_save_failure(err)

    # Read it back in a *fresh* session (empty identity map, so a real SELECT
    # of committed rows), so a 200 here means the data really is in the DB.
    try:
        with db_session:
            if not visit_exists(tz, visit_date):
                raise _save_error(
                    500, "verify_missing",
                    "The save reported success, but the visit could not be found in the database "
                    "afterwards. Treat it as NOT saved and save again.",
                )
            v, procs, diags = get_visit(tz, visit_date)
            return _visit_out(v, procs, diags, visit_date, is_new=False)
    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Re-reading visit %s/%s after save failed", tz, visit_date)
        raise _save_error(
            503, "verify_failed",
            f"The visit was committed, but reading it back to confirm failed ({type(err).__name__}: {err}). "
            f"It was probably saved -- reopen the visit to check before re-entering anything.",
        )


@api_router.delete("/patients/{tz}/visits/{visit_date}", status_code=204)
def delete_visit_route(tz: str, visit_date: datetime.date, user: dict = Depends(require_login_api)):
    with db_session:
        _require_patient(tz)
        is_admin = user.get("role") == "admin"
        if visit_date != datetime.date.today() and not is_admin:
            raise HTTPException(403, "You can delete a visit only from today (unless you're an admin).")
        if not visit_exists(tz, visit_date):
            raise HTTPException(404, "Visit not found")
        ret = delete_visit(tz, visit_date)
        if ret != 0:  # error_codes.ERR_OK
            raise HTTPException(400, "Could not delete visit.")


@api_router.get("/patients/{tz}/visits/{visit_date}/report", response_class=HTMLResponse)
def get_visit_report(tz: str, visit_date: datetime.date):
    """Full standalone HTML report -- equivalent of Visits/visits.py's
    review_summary(). No today-only restriction: the Qt app lets you pull a
    summary for any past visit too. Used as-is for the in-page preview, as
    the target of the print/PDF flow (browser print dialog on this page),
    and as the payload for the "download as HTML" option -- one endpoint
    covers all three since the client just does something different with
    the same HTML string.
    """
    with db_session:
        _require_patient(tz)
        p = PatientCore[tz]
        fname, surname = p.fname, p.surname
        report = Report(tz, visit_date, surname, fname)
        html = report_header + report.get_string() + report_tail
    for filename in REPORT_IMAGES:
        # Match by filename only, not the full file:// path -- Config/config.toml
        # hardcodes an absolute path from the machine it was authored on
        # (file:///home/dwende/repo/clinic/...), which is *not* REPO_ROOT on any
        # other deployment (e.g. /home/dietpi/clinic on the Pi). A literal
        # f"file://{REPO_ROOT / filename}" match only ever worked by coincidence
        # on the original dev machine; matching solely on the trailing filename
        # works regardless of where the server (or config.toml's author) lives.
        html = re.sub(rf'file://\S*/{re.escape(filename)}', f"/report-assets/{filename}", html)
    # The page <title> is what browsers suggest as the filename for
    # "Save as PDF" in the print dialog -- there's no other way to hint a
    # default filename there. Config/config.toml's header hardcodes a
    # generic "<title > Patient Summary </title>"; replace it (regex, not
    # a literal match, since the exact whitespace in that string is a bit
    # unusual) so Print / Save as PDF suggests "{tz}_{YYYYMMDD}.pdf".
    html = re.sub(
        r"<title.*?>.*?</title>",
        f"<title>{_report_filename_stem(tz, visit_date)}</title>",
        html,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return HTMLResponse(content=html)


@api_router.get("/procedures", response_model=list[str])
def list_all_procedures():
    """Distinct procedure names across all visits, for the picker/autocomplete."""
    with db_session:
        return list(get_all_procedures())


@api_router.get("/diagnoses", response_model=list[str])
def list_all_diagnoses():
    """Distinct diagnosis names across all visits, for the picker/autocomplete."""
    with db_session:
        return list(dict(get_all_diagnoses()).keys())
