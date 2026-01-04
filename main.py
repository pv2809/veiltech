from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from core.db import get_db

app = FastAPI(title="VeilTech API")

# --------------------
# Response Models
# --------------------
class StatusResponse(BaseModel):
    status: str

class AuthResponse(BaseModel):
    message: str
    firebase_uid: str

# --------------------
# Health
# --------------------
@app.get("/", response_model=StatusResponse)
def root():
    return {"status": "alive"}

@app.get("/ping", response_model=StatusResponse)
def ping():
    return {"status": "ok"}

# --------------------
# Register
# --------------------
@app.post("/register", response_model=AuthResponse)
def register_user(
    firebase_uid: str = Form(..., min_length=3),
    phone: str = Form(..., min_length=8),
):
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE firebase_uid = %s",
            (firebase_uid,)
        )
        existing = cursor.fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="User already registered"
            )

        cursor.execute(
            "INSERT INTO users (firebase_uid, phone) VALUES (%s, %s)",
            (firebase_uid, phone)
        )
        db.commit()

        return {
            "message": "registration successful",
            "firebase_uid": firebase_uid
        }

    finally:
        cursor.close()
        db.close()

# --------------------
# Login
# --------------------
@app.post("/login", response_model=AuthResponse)
def login_user(
    firebase_uid: str = Form(...),
):
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE firebase_uid = %s",
            (firebase_uid,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not registered"
            )

        return {
            "message": "login successful",
            "firebase_uid": firebase_uid
        }

    finally:
        cursor.close()
        db.close()
