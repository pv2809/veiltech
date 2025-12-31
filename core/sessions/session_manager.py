from datetime import datetime, timedelta
import uuid
from core.db import get_db

SESSION_TIMEOUT = timedelta(minutes=3)

def create_session(user_id: str) -> str:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    session_id = str(uuid.uuid4())
    now = datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO sessions (session_id, user_id, last_activity, active)
        VALUES (%s, %s, %s, TRUE)
        """,
        (session_id, user_id, now)
    )
    db.commit()
    db.close()

    return session_id


def validate_session(session_id: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM sessions WHERE session_id=%s AND active=TRUE",
        (session_id,)
    )
    session = cursor.fetchone()

    if not session:
        db.close()
        return None

    if datetime.utcnow() - session["last_activity"] > SESSION_TIMEOUT:
        cursor.execute(
            "UPDATE sessions SET active=FALSE WHERE session_id=%s",
            (session_id,)
        )
        db.commit()
        db.close()
        return None

    cursor.execute(
        "UPDATE sessions SET last_activity=%s WHERE session_id=%s",
        (datetime.utcnow(), session_id)
    )
    db.commit()
    db.close()

    return session["user_id"]


def invalidate_session(session_id: str):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE sessions SET active=FALSE WHERE session_id=%s",
        (session_id,)
    )
    db.commit()
    db.close()
