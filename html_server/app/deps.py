from fastapi import HTTPException, Request, status


def get_current_user(request: Request) -> dict | None:
    return request.session.get("user")


def require_login_page(request: Request) -> dict:
    """Dependency for HTML page routes: bounce to /login if not signed in."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user


def require_login_api(request: Request) -> dict:
    """Dependency for JSON API routes: 401 instead of a redirect."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
