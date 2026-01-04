from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from core.db import get_db

app = FastAPI(title="VeilTech API", version="1.0.0")

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
@app.get("/", response_model=StatusResponse, tags=["Health"])
def root():
    return {"status": "alive"}

@app.get("/ping", response_model=StatusResponse, tags=["Health"])
def ping():
    return {"status": "ok"}

# --------------------
# Register
# --------------------
@app.post("/register", response_model=AuthResponse, tags=["Auth"])
def register_user(
    firebase_uid: str = Form(..., min_length=3),
    phone: str = Form(..., min_length=8, max_length=15),
):
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    cursor = None
    try:
        cursor = db.cursor(dictionary=True)

        # ✅ use correct primary key
        cursor.execute(
            "SELECT user_id FROM users WHERE firebase_uid = %s",
            (firebase_uid,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail="User already registered"
            )

        cursor.execute(
            """
            INSERT INTO users (firebase_uid, phone)
            VALUES (%s, %s)
            """,
            (firebase_uid, phone)
        )
        db.commit()

        return {
            "message": "registration successful",
            "firebase_uid": firebase_uid
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail="Registration failed")

    finally:
        if cursor:
            cursor.close()
        db.close()

# --------------------
# Login
# --------------------
@app.post("/login", response_model=AuthResponse, tags=["Auth"])
def login_user(
    firebase_uid: str = Form(...),
):
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    cursor = None
    try:
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id FROM users WHERE firebase_uid = %s",
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

    except HTTPException:
        raise

    except Exception as e:
        print("❌ LOGIN ERROR:", e)
        raise HTTPException(status_code=500, detail="Login failed")

    finally:
        if cursor:
            cursor.close()
        db.close()
