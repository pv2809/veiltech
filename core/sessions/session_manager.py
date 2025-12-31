from datetime import datetime, timedelta
import uuid
import mysql.connector

SESSION_TIMEOUT = timedelta(minutes=3)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="7815",
    database="veiltech"
)
cursor = db.cursor(dictionary=True)


def create_session(user_email: str) -> str:
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO sessions (session_id, user_email, last_activity, active)
        VALUES (%s, %s, %s, TRUE)
        """,
        (session_id, user_email, now)
    )
    db.commit()

    return session_id


def validate_session(session_id: str) -> str | None:
    cursor.execute(
        "SELECT * FROM sessions WHERE session_id=%s AND active=TRUE",
        (session_id,)
    )
    session = cursor.fetchone()

    if not session:
        return None

    last_activity = session["last_activity"]
    if datetime.utcnow() - last_activity > SESSION_TIMEOUT:
        cursor.execute(
            "UPDATE sessions SET active=FALSE WHERE session_id=%s",
            (session_id,)
        )
        db.commit()
        return None

    # update activity timestamp
    cursor.execute(
        "UPDATE sessions SET last_activity=%s WHERE session_id=%s",
        (datetime.utcnow(), session_id)
    )
    db.commit()

    return session["user_email"]


def invalidate_session(session_id: str):
    cursor.execute(
        "UPDATE sessions SET active=FALSE WHERE session_id=%s",
        (session_id,)
    )
    db.commit()
