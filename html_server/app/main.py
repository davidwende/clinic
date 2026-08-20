from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth.routes import router as auth_router
from app.blood.routes import api_router as blood_api_router
from app.blood.routes import page_router as blood_page_router
from app.config import SECRET_KEY, SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS, STATIC_DIR
from app.diag_proc.routes import api_router as diag_proc_api_router
from app.diag_proc.routes import page_router as diag_proc_page_router
from app.past_history.routes import api_router as past_history_api_router
from app.past_history.routes import page_router as past_history_page_router
from app.patients.routes import api_router as patients_api_router
from app.patients.routes import page_router as patients_page_router
from app.visits.routes import api_router as visits_api_router
from app.visits.routes import page_router as visits_page_router

app = FastAPI(title="Clinic")

# https_only defaults to False so this also works over plain HTTP during
# local/LAN dev. Set it True (and terminate TLS in front of uvicorn, e.g.
# nginx) before this is reachable outside a trusted local network -- the
# session cookie is the entire auth mechanism.
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIE_NAME,
    max_age=SESSION_MAX_AGE_SECONDS,
    same_site="lax",
    https_only=False,
)

class RevalidateStaticFiles(StaticFiles):
    """Starlette's StaticFiles already supports conditional requests
    (ETag/Last-Modified -> 304), but sets no Cache-Control header, so
    browsers fall back to their own heuristic caching and can serve a
    stale JS/CSS file for a while after a change with no revalidation at
    all -- the exact "hard refresh needed" surprise this exists to avoid.
    no-cache still allows caching, it just forces a revalidation check on
    every load, which is cheap (a 304 if unchanged) given this app's file
    sizes and the fact that it's a handful of clients on a LAN, not a
    public site under real load.
    """

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response


app.mount("/static", RevalidateStaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router)
app.include_router(patients_page_router)
app.include_router(patients_api_router)
app.include_router(past_history_page_router)
app.include_router(past_history_api_router)
app.include_router(visits_page_router)
app.include_router(visits_api_router)
app.include_router(blood_page_router)
app.include_router(blood_api_router)
app.include_router(diag_proc_page_router)
app.include_router(diag_proc_api_router)


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse("/patients", status_code=303)
