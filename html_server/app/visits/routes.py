import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import REPO_ROOT, TEMPLATES_DIR
from app.db import db_session
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


@api_router.put("/patients/{tz}/visits/{visit_date}", response_model=VisitOut)
def save_visit_route(tz: str, visit_date: datetime.date, body: VisitIn):
    with db_session:
        _require_patient(tz)
        if visit_date != datetime.date.today():
            raise HTTPException(400, "You can save/modify a visit only from today.")

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

        ret = save_visit(
            tz, visit_date, cc, loc, back, knee, ankle, anklest,
            hip, neck, shoulder, exam, tests, body.procedures, body.diagnoses, recommend,
        )
        if ret != 0:  # error_codes.ERR_OK
            raise HTTPException(400, "Could not save visit data.")

        v, procs, diags = get_visit(tz, visit_date)
        return _visit_out(v, procs, diags, visit_date, is_new=False)


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
        html = html.replace(f"file://{REPO_ROOT / filename}", f"/report-assets/{filename}")
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
