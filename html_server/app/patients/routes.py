import datetime
import string

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.db import db_session
from app.deps import require_login_api, require_login_page
from app.schemas import PatientIn, PatientOut, PatientSummary, TzChangeIn, VisitSummaryOut
from app.validation import validate_email_address, validate_phone, validate_tz

from Database.dbCreate import PatientCore
from Database.dbFuncs import (
    delete_patient as db_delete_patient,
)
from Database.dbFuncs import (
    get_all_patients,
    modify_patient,
    modify_patient_tz,
    num_visits,
    patient_exists,
    save_new_patient,
    visits_between_dates,
    visits_with_procedures_between_dates,
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

page_router = APIRouter(tags=["patients-page"])
api_router = APIRouter(
    prefix="/api/patients", tags=["patients-api"], dependencies=[Depends(require_login_api)]
)


# ---------------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------------

@page_router.get("/patients")
def patients_page(request: Request, user: dict = Depends(require_login_page)):
    return templates.TemplateResponse(request, "patients.html", {"user": user})


# ---------------------------------------------------------------------------
# JSON API -- mirrors Application_Main/main.py's MainWindow patient panel
# ---------------------------------------------------------------------------

def _patient_out(p: PatientCore) -> PatientOut:
    return PatientOut(
        tz=p.tz,
        fname=p.fname,
        surname=p.surname,
        email=p.email,
        phone=p.phone_number,
        dob=p.dob,
        male=p.male,
        smoker=p.smoking,
        consent=p.consent,
        visit_count=len(p.visits),
    )


def _validate_patient_fields(
    tz: str, fname: str, surname: str, email: str, phone: str, dob: datetime.date,
    *, is_create: bool, force_tz: bool,
) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not validate_tz(tz) and not force_tz:
        errors["tz"] = "Invalid Israeli ID checksum. Retry with force_tz=true to save anyway."
    if not fname.strip():
        errors["fname"] = "First name is required."
    if not surname.strip():
        errors["surname"] = "Surname is required."
    if not validate_email_address(email):
        errors["email"] = "Invalid email address."
    if not validate_phone(phone):
        errors["phone"] = "Invalid phone number."
    if dob > datetime.date.today():
        errors["dob"] = "Date of birth is in the future."
    if is_create and patient_exists(tz):
        errors["tz"] = "A patient with this ID already exists."
    return errors


@api_router.get("", response_model=list[PatientSummary])
def list_patients(q: str = Query("", description="Matched against ID / first / last name")):
    with db_session:
        rows = get_all_patients()
    needle = q.strip().lower()
    results = [
        PatientSummary(tz=tz, fname=fname, surname=surname, visit_count=visit_count)
        for visit_count, tz, fname, surname in rows
        if not needle or needle in f"{tz} {fname} {surname}".lower()
    ]
    results.sort(key=lambda p: (p.surname.lower(), p.fname.lower()))
    return results


@api_router.get("/summary", response_model=VisitSummaryOut)
def visit_summary(
    date_from: datetime.date = Query(..., alias="from"),
    date_to: datetime.date = Query(..., alias="to"),
):
    with db_session:
        return VisitSummaryOut(
            visits=visits_between_dates(date_from, date_to),
            visits_with_procedures=visits_with_procedures_between_dates(date_from, date_to),
        )


@api_router.get("/{tz}", response_model=PatientOut)
def get_patient(tz: str):
    with db_session:
        p = PatientCore.get(tz=tz)
        if not p:
            raise HTTPException(404, "Patient not found")
        return _patient_out(p)


@api_router.post("", response_model=PatientOut, status_code=201)
def create_patient(patient: PatientIn, force_tz: bool = Query(False)):
    with db_session:
        errors = _validate_patient_fields(
            patient.tz, patient.fname, patient.surname, patient.email,
            patient.phone, patient.dob, is_create=True, force_tz=force_tz,
        )
        if errors:
            raise HTTPException(422, detail=errors)
        save_new_patient(
            patient.tz,
            string.capwords(patient.fname.strip()),
            string.capwords(patient.surname.strip()),
            patient.email.strip(),
            patient.phone.strip(),
            patient.smoker,
            patient.dob,
            patient.male,
            patient.consent,
        )
        return _patient_out(PatientCore[patient.tz])


@api_router.put("/{tz}", response_model=PatientOut)
def update_patient(tz: str, patient: PatientIn, force_tz: bool = Query(False)):
    with db_session:
        if not patient_exists(tz):
            raise HTTPException(404, "Patient not found")
        if patient.tz != tz:
            raise HTTPException(400, "Changing the ID here is not supported; use the /tz endpoint.")
        errors = _validate_patient_fields(
            tz, patient.fname, patient.surname, patient.email,
            patient.phone, patient.dob, is_create=False, force_tz=force_tz,
        )
        if errors:
            raise HTTPException(422, detail=errors)
        modify_patient(
            tz,
            string.capwords(patient.fname.strip()),
            string.capwords(patient.surname.strip()),
            patient.email.strip(),
            patient.phone.strip(),
            patient.smoker,
            patient.dob,
            patient.male,
            patient.consent,
        )
        return _patient_out(PatientCore[tz])


@api_router.delete("/{tz}", status_code=204)
def remove_patient(tz: str):
    with db_session:
        if not patient_exists(tz):
            raise HTTPException(404, "Patient not found")
        if num_visits(tz) > 0:
            raise HTTPException(409, "Cannot delete a patient with recorded visits.")
        db_delete_patient(tz)


@api_router.post("/{tz}/tz", response_model=PatientOut)
def change_tz(tz: str, body: TzChangeIn):
    with db_session:
        if not patient_exists(tz):
            raise HTTPException(404, "Patient not found")
        new_tz = body.new_tz.strip()
        if len(new_tz) != 9 or not new_tz.isdigit():
            raise HTTPException(422, detail={"new_tz": "TZ must be exactly 9 digits."})
        if patient_exists(new_tz):
            raise HTTPException(409, detail={"new_tz": "A patient with this ID already exists."})
        if not modify_patient_tz(tz, new_tz):
            raise HTTPException(409, detail={"new_tz": "Could not change ID."})
        return _patient_out(PatientCore[new_tz])
