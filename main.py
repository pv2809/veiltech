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
# Health Routes
# --------------------
@app.get("/", response_model=StatusResponse)
def root():
    return {"status": "alive"}

@app.get("/ping", response_model=StatusResponse)
def ping():
    return {"status": "ok"}

# --------------------
# Auth Route
# --------------------
@app.post("/auth", response_model=AuthResponse)
def auth_user(
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
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (firebase_uid, phone) VALUES (%s, %s)",
                (firebase_uid, phone)
            )
            db.commit()

        return {
            "message": "login success",
            "firebase_uid": firebase_uid
        }

    except Exception as e:
        print("❌ AUTH ERROR:", e)
        raise HTTPException(status_code=500, detail="Auth failed")

    finally:
        cursor.close()
        db.close()
