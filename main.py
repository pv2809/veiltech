from fastapi import FastAPI, Form, HTTPException
from core.db import get_db

app = FastAPI()


@app.get("/")
def root():
    return {"status": "alive"}


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/auth")
def auth_user(
    firebase_uid: str = Form(...),
    phone: str = Form(...)
):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE firebase_uid = %s",
            (firebase_uid,)
        )
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (firebase_uid, phone) VALUES (%s, %s)",
                (firebase_uid, phone)
            )
            db.commit()

        cursor.close()
        db.close()

        return {
            "message": "login success",
            "firebase_uid": firebase_uid
        }

    except Exception as e:
        print("❌ AUTH ERROR:", e)
        raise HTTPException(status_code=500, detail="Auth failed")
