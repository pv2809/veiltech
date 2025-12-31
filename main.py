from fastapi import FastAPI, HTTPException, Form, Request, Header
import mysql.connector
import time
from core.sessions.session_manager import invalidate_session, create_session
from core.sessions.session_middleware import require_session
import os
app = FastAPI()

# ---------- DATABASE ----------
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
# ---------- PING ----------
@app.get("/ping")
def ping():
    return {"status": "connected"}

# ---------- AUTH (PHONE OTP ONLY) ----------
@app.post("/auth")
def auth_user(
    firebase_uid: str = Form(...),
    phone: str = Form(...)
):
    try:
        cursor.execute(
            "SELECT * FROM users WHERE firebase_uid=%s",
            (firebase_uid,)
        )
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (firebase_uid, phone) VALUES (%s, %s)",
                (firebase_uid, phone)
            )
            db.commit()

        # 🔐 Create session using phone as identity
        session_id = create_session(phone)

        return {
            "message": "login success",
            "session_id": session_id
        }

    except Exception as e:
        print("AUTH ERROR:", e)
        raise HTTPException(status_code=500, detail="Internal")

# ---------- SECURE ----------
@app.get("/secure-data")
def secure_data(
    request: Request,
    x_session_id: str = Header(..., alias="X-Session-ID")
):
    user = require_session(request)
    return {"message": f"Access granted to {user}"}

# ---------- REGISTER FILE ----------
@app.post("/register-file")
def register_file(
    request: Request,
    file_id: str = Form(...),
    expiry_seconds: int = Form(...),
    max_views: int = Form(...)
):
    owner = require_session(request)

    cursor.execute(
        """
        INSERT INTO secure_files
        (id, owner, created_at, expiry_seconds, max_views)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (file_id, owner, int(time.time()), expiry_seconds, max_views)
    )
    db.commit()

    return {"status": "REGISTERED"}

# ---------- REVEAL FILE ----------
@app.post("/reveal")
def reveal_file(file_id: str = Form(...)):
    cursor.execute("SELECT * FROM secure_files WHERE id=%s", (file_id,))
    record = cursor.fetchone()

    if not record:
        raise HTTPException(404, "FILE_NOT_FOUND")

    now = int(time.time())

    if record["locked"]:
        raise HTTPException(403, "FILE_LOCKED")

    if now > record["created_at"] + record["expiry_seconds"]:
        raise HTTPException(410, "FILE_EXPIRED")

    if record["views_used"] >= record["max_views"]:
        raise HTTPException(403, "MAX_VIEWS_REACHED")

    cursor.execute(
        "UPDATE secure_files SET views_used = views_used + 1 WHERE id=%s",
        (file_id,)
    )
    db.commit()

    return {"status": "ACCESS_GRANTED"}

# ---------- LOGOUT ----------
@app.post("/logout")
def logout(request: Request):
    session_id = request.headers.get("X-Session-ID")

    if session_id:
        invalidate_session(session_id)

    return {"status": "LOGGED_OUT"}
