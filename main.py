import random
import hashlib
from datetime import datetime, timedelta

from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from core.db import get_db

app = FastAPI(title="VeilTech API", version="1.0.0")

# --------------------
# Models
# --------------------
class StatusResponse(BaseModel):
    status: str

class AuthResponse(BaseModel):
    message: str
    phone: str
    is_new_user: bool

# --------------------
# Helpers
# --------------------
def generate_otp():
    return str(random.randint(100000, 999999))

def hash_otp(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()

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
# Request OTP (LOGIN / REGISTER)
# --------------------
@app.post("/auth/request-otp")
def request_otp(
    phone: str = Form(..., min_length=8, max_length=15)
):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    otp = generate_otp()
    otp_hash = hash_otp(otp)
    expires_at = datetime.utcnow() + timedelta(minutes=1)  # ⏱️ 1 min validity

    try:
        cursor.execute(
            """
            INSERT INTO otp_requests (phone, otp_hash, expires_at, attempts)
            VALUES (%s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
                otp_hash=%s,
                expires_at=%s,
                attempts=0
            """,
            (phone, otp_hash, expires_at, otp_hash, expires_at)
        )
        db.commit()

        # TEMP (replace with SMS provider)
        print(f"📩 OTP for {phone}: {otp}")

        return {"message": "OTP sent (required for login & registration)"}

    finally:
        cursor.close()
        db.close()

# --------------------
# Verify OTP → LOGIN OR REGISTER
# --------------------
@app.post("/auth/verify-otp", response_model=AuthResponse)
def verify_otp(
    phone: str = Form(...),
    otp: str = Form(...)
):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # 🔍 Fetch OTP record
        cursor.execute(
            "SELECT * FROM otp_requests WHERE phone=%s",
            (phone,)
        )
        record = cursor.fetchone()

        if not record:
            raise HTTPException(400, "OTP not requested")

        if record["attempts"] >= 3:
            raise HTTPException(429, "OTP attempts exceeded")

        if datetime.utcnow() > record["expires_at"]:
            raise HTTPException(400, "OTP expired")

        if hash_otp(otp) != record["otp_hash"]:
            cursor.execute(
                "UPDATE otp_requests SET attempts = attempts + 1 WHERE phone=%s",
                (phone,)
            )
            db.commit()
            raise HTTPException(401, "Invalid OTP")

        # ✅ OTP VALID → Check user
        cursor.execute(
            "SELECT user_id FROM users WHERE phone=%s",
            (phone,)
        )
        user = cursor.fetchone()

        if user:
            is_new_user = False
        else:
            # 🆕 Register new user
            cursor.execute(
                "INSERT INTO users (phone) VALUES (%s)",
                (phone,)
            )
            db.commit()
            is_new_user = True

        # 🧹 Remove OTP after success
        cursor.execute(
            "DELETE FROM otp_requests WHERE phone=%s",
            (phone,)
        )
        db.commit()

        return {
            "message": "authentication successful",
            "phone": phone,
            "is_new_user": is_new_user
        }

    finally:
        cursor.close()
        db.close()

# --------------------
# Resend OTP
# --------------------
@app.post("/auth/resend-otp")
def resend_otp(
    phone: str = Form(..., min_length=8, max_length=15)
):
    return request_otp(phone)
