from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.db import db_session
from app.deps import require_login_api, require_login_page
from app.schemas import PatientBasicOut

from Database.dbFuncs import get_patients_by_diagnosis, get_patients_by_procedure

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

page_router = APIRouter(tags=["diag-proc-page"])
api_router = APIRouter(prefix="/api", tags=["diag-proc-api"], dependencies=[Depends(require_login_api)])


# ---------------------------------------------------------------------------
# HTML page -- unlike every other module, this one isn't tied to a patient.
# Equivalent of DiagProcWindow, which MainWindow.show_diag_proc() opens with
# no arguments and no "choose a patient first" guard.
# ---------------------------------------------------------------------------

@page_router.get("/diag-proc")
def diag_proc_page(request: Request, user: dict = Depends(require_login_page)):
    return templates.TemplateResponse(request, "diag_proc.html", {"user": user})


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------

@api_router.get("/diag-proc/patients", response_model=list[PatientBasicOut])
def patients_by_diag_or_proc(diagnosis: str | None = None, procedure: str | None = None):
    """Union of patients matching the selected diagnosis and/or procedure --
    matches DiagProcWindow.update_patients_list(), which adds both result
    sets into one `set()` rather than intersecting them.
    """
    with db_session:
        patients = set()
        if diagnosis:
            patients.update(get_patients_by_diagnosis(diagnosis))
        if procedure:
            patients.update(get_patients_by_procedure(procedure))
        return [
            PatientBasicOut(tz=tz, fname=fname, surname=surname)
            for tz, fname, surname in sorted(patients)
        ]
