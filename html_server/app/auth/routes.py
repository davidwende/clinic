from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.deps import get_current_user
from app.user_store import verify_user

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/login")
def login_form(request: Request):
    if get_current_user(request):
        return RedirectResponse("/patients", status_code=303)
    return templates.TemplateResponse(
        request, "login.html", {"error": None}
    )


@router.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    user = verify_user(username.strip(), password)
    if not user:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Incorrect username or password."},
            status_code=401,
        )
    request.session["user"] = user
    return RedirectResponse("/patients", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
