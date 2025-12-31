from fastapi import Request, HTTPException
from core.sessions.session_manager import validate_session


def require_session(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        raise HTTPException(status_code=401, detail="Session missing")

    user_email = validate_session(session_id)

    if not user_email:
        raise HTTPException(status_code=401, detail="Session expired")

    return user_email
