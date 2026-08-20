from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.db import db_session
from app.deps import require_login_api, require_login_page
from app.schemas import PastHistoryIn, PastHistoryOut

from Database.dbCreate import PatientCore
from Database.dbFuncs import (
    get_acs,
    get_all_acs,
    get_all_nacs,
    get_nacs,
    get_past_history,
    patient_exists,
    save_acs,
    save_nacs,
    save_patient_history,
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

page_router = APIRouter(tags=["past-history-page"])
api_router = APIRouter(prefix="/api", tags=["past-history-api"], dependencies=[Depends(require_login_api)])


# ---------------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------------

@page_router.get("/patients/{tz}/history")
def past_history_page(tz: str, request: Request, user: dict = Depends(require_login_page)):
    with db_session:
        p = PatientCore.get(tz=tz)
        if not p:
            raise HTTPException(404, "Patient not found")
        context = {"user": user, "tz": tz, "fname": p.fname, "surname": p.surname}
    return templates.TemplateResponse(request, "past_history.html", context)


# ---------------------------------------------------------------------------
# JSON API -- mirrors Past_History/PastHistory.py's PastHistoryForm
# ---------------------------------------------------------------------------

def _history_out(tz: str) -> PastHistoryOut:
    ph = get_past_history(tz)
    if ph is None:
        return PastHistoryOut(nacs=list(get_nacs(tz)), acs=list(get_acs(tz)))
    return PastHistoryOut(
        hypertension=ph.hypertension,
        diabetes=ph.diabetes,
        blood=ph.blood,
        blood_descr=ph.blood_descr or "",
        malignancy=ph.malignancy,
        malignancy_date=ph.malignancy_date or "",
        malignancy_details=ph.malignancy_details or "",
        malignancy_remiss=ph.malignancy_remiss,
        disable=ph.disable,
        disable_details=ph.disable_details or "",
        operations=ph.operations or "",
        trauma=ph.trauma or "",
        nacs=list(get_nacs(tz)),
        acs=list(get_acs(tz)),
    )


@api_router.get("/patients/{tz}/history", response_model=PastHistoryOut)
def get_history(tz: str):
    with db_session:
        if not patient_exists(tz):
            raise HTTPException(404, "Patient not found")
        return _history_out(tz)


@api_router.put("/patients/{tz}/history", response_model=PastHistoryOut)
def update_history(tz: str, body: PastHistoryIn):
    with db_session:
        if not patient_exists(tz):
            raise HTTPException(404, "Patient not found")
        save_patient_history(
            tz,
            body.hypertension,
            body.diabetes,
            body.blood,
            body.blood_descr,
            body.malignancy,
            body.malignancy_date,
            body.malignancy_details,
            body.malignancy_remiss,
            body.disable,
            body.disable_details,
            body.operations,
            body.trauma,
        )
        # Unlike the Qt form (which only calls save_nacs/save_acs when its
        # nacs_changed/acs_changed flags are set), we always overwrite both
        # lists with whatever the client sent -- simpler, and the outcome is
        # identical since the client always sends the full current list.
        save_nacs(tz, body.nacs)
        save_acs(tz, body.acs)
        return _history_out(tz)


@api_router.get("/nacs", response_model=list[str])
def list_all_nacs():
    """Distinct NAC medication names across all patients, for autocomplete."""
    with db_session:
        return list(get_all_nacs())


@api_router.get("/acs", response_model=list[str])
def list_all_acs():
    """Distinct AC medication names across all patients, for autocomplete."""
    with db_session:
        return list(get_all_acs())
