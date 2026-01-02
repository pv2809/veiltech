from fastapi import FastAPI, Form
from core.db import get_db
from core.sessions.session_manager import create_session

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/auth")
def auth_user(firebase_uid: str = Form(...), phone: str = Form(...)):
    db = get_db()
    cursor = db.cursor(dictionary=True)

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

    cursor.close()
    db.close()

    session_id = create_session(firebase_uid)

    return {
        "message": "login success",
        "session_id": session_id
    }
