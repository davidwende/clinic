import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.db import db_session
from app.deps import require_login_api, require_login_page
from app.schemas import BloodReadingIn, BloodReadingOut

from Database.dbCreate import PatientCore
from Database.dbFuncs import add_blood_to_db, delete_blood_from_db, get_all_blood, patient_exists

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

page_router = APIRouter(tags=["blood-page"])
api_router = APIRouter(prefix="/api", tags=["blood-api"], dependencies=[Depends(require_login_api)])


def _require_patient(tz: str) -> None:
    if not patient_exists(tz):
        raise HTTPException(404, "Patient not found")


PULSE_MAX = 200
SYSTOLIC_MAX = 254
DIASTOLIC_MAX = 120


def _validate_reading(pulse: int | None, systolic: int | None, diastolic: int | None) -> str | None:
    """Mirrors Blood/blood.py's check_blood -- same thresholds, same
    both-or-neither rule for systolic/diastolic, same at-least-one rule --
    plus a negative-value check check_blood doesn't have, and messages
    that spell out the actual value and threshold rather than just "too
    high"/"not valid". check_blood itself isn't importable here:
    Blood/blood.py pulls in PySide6 at module level, which html_server
    doesn't depend on.

    The negative check matters now that BloodPulse.pulse/systolic/diastolic
    are unsigned columns (Database/dbCreate.py) -- without it, a negative
    value would sail past here and fail as a raw, unhandled ValueError from
    Pony's own column-bounds check instead of a clean 422.
    """
    for label, value in (("Pulse", pulse), ("Systolic", systolic), ("Diastolic", diastolic)):
        if value is not None and value < 0:
            return f"{label} can't be negative -- got {value}."

    if pulse is not None and pulse > PULSE_MAX:
        return f"Pulse of {pulse} is too high -- must be {PULSE_MAX} or less."
    if systolic is not None and systolic > SYSTOLIC_MAX:
        return f"Systolic of {systolic} is too high -- must be {SYSTOLIC_MAX} or less."
    if diastolic is not None and diastolic > DIASTOLIC_MAX:
        return f"Diastolic of {diastolic} is too high -- must be {DIASTOLIC_MAX} or less."

    if (systolic is not None) != (diastolic is not None):
        have_label, have_val = ("Systolic", systolic) if systolic is not None else ("Diastolic", diastolic)
        missing_label = "diastolic" if systolic is not None else "systolic"
        return f"You entered {have_label.lower()} ({have_val}) but no {missing_label} -- both are required together."

    if pulse is None and systolic is None and diastolic is None:
        return "Enter at least a pulse rate, or a full blood pressure reading (systolic and diastolic)."

    return None


# ---------------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------------

@page_router.get("/patients/{tz}/blood")
def blood_page(tz: str, request: Request, user: dict = Depends(require_login_page)):
    with db_session:
        p = PatientCore.get(tz=tz)
        if not p:
            raise HTTPException(404, "Patient not found")
        context = {"user": user, "tz": tz, "fname": p.fname, "surname": p.surname}
    return templates.TemplateResponse(request, "blood.html", context)


# ---------------------------------------------------------------------------
# JSON API -- mirrors Blood/blood.py's BloodForm
# ---------------------------------------------------------------------------

@api_router.get("/patients/{tz}/blood/{visit_date}", response_model=list[BloodReadingOut])
def list_blood_readings(tz: str, visit_date: datetime.date):
    with db_session:
        _require_patient(tz)
        # get_all_blood silently creates a blank Visits row for visit_date
        # if none exists yet -- same as the Qt app, and required so a
        # reading can be added later without filling out the exam form
        # first (add_blood_to_db does a direct Visits[tz, date] lookup).
        readings = get_all_blood(tz, visit_date)
        return [
            BloodReadingOut(time=t, pulse=pulse, systolic=systolic, diastolic=diastolic)
            for t, pulse, systolic, diastolic in readings
        ]


@api_router.post("/patients/{tz}/blood/{visit_date}", response_model=list[BloodReadingOut], status_code=201)
def add_blood_reading(tz: str, visit_date: datetime.date, body: BloodReadingIn):
    with db_session:
        _require_patient(tz)
        if visit_date != datetime.date.today():
            raise HTTPException(400, "Can't add to a date that is not today.")
        error = _validate_reading(body.pulse, body.systolic, body.diastolic)
        if error:
            raise HTTPException(422, error)

        get_all_blood(tz, visit_date)  # ensures the Visits row exists
        add_blood_to_db(
            tz, visit_date, datetime.datetime.now().time(),
            body.pulse, body.systolic, body.diastolic,
        )
        readings = get_all_blood(tz, visit_date)
        return [
            BloodReadingOut(time=t, pulse=pulse, systolic=systolic, diastolic=diastolic)
            for t, pulse, systolic, diastolic in readings
        ]


@api_router.delete("/patients/{tz}/blood/{visit_date}/{reading_time}", status_code=204)
def delete_blood_reading(
    tz: str, visit_date: datetime.date, reading_time: datetime.time,
    user: dict = Depends(require_login_api),
):
    with db_session:
        _require_patient(tz)
        is_admin = user.get("role") == "admin"
        if visit_date != datetime.date.today() and not is_admin:
            raise HTTPException(403, "You can delete a reading only from today (unless you're an admin).")
        ret = delete_blood_from_db(tz, visit_date, reading_time)
        if ret != 0:  # error_codes.ERR_OK
            raise HTTPException(404, "Reading not found")
