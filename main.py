from fastapi import FastAPI, Form, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

from core.db import get_db
from core.firebase import verify_firebase_token

app = FastAPI(title="VeilTech API", version="1.0.0")

# --------------------
# Response Models
# --------------------
class StatusResponse(BaseModel):
    status: str

class AuthResponse(BaseModel):
    message: str
    session_token: str
    is_new_user: bool

# --------------------
# Health
# --------------------
@app.get("/", response_model=StatusResponse, tags=["Health"])
def root():
    return {"status": "alive"}

@app.get("/ping", response_model=StatusResponse, tags=["Health"])
def ping():
    return {"status": "ok"}

# --------------------
# Firebase OTP Auth (LOGIN + REGISTER)
# --------------------
@app.post("/auth/firebase", response_model=AuthResponse, tags=["Auth"])
def auth_with_firebase(
    id_token: str = Form(...)
):
    # 1️⃣ Verify Firebase ID token
    try:
        decoded = verify_firebase_token(id_token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase token"
        )

    phone = decoded.get("phone_number")
    if not phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number not found in Firebase token"
        )

    # 2️⃣ Connect DB
    db = get_db()
    if not db:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )

    cursor = db.cursor(dictionary=True)

    try:
        # 3️⃣ Check if user exists
        cursor.execute(
            "SELECT user_id FROM users WHERE phone=%s",
            (phone,)
        )
        user = cursor.fetchone()

        if user:
            user_id = user["user_id"]
            is_new_user = False
        else:
            # 4️⃣ Register new user
            cursor.execute(
                "INSERT INTO users (phone) VALUES (%s)",
                (phone,)
            )
            db.commit()
            user_id = cursor.lastrowid
            is_new_user = True

        # 5️⃣ Create session token
        session_token = secrets.token_hex(32)
        expires_at = datetime.utcnow() + timedelta(hours=12)

        cursor.execute(
            """
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, session_token, expires_at)
        )
        db.commit()

        return {
            "message": "authentication successful",
            "session_token": session_token,
            "is_new_user": is_new_user
        }

    finally:
        cursor.close()
        db.close()
