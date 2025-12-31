from datetime import datetime, timedelta
import uuid
import os
import mysql.connector

SESSION_TIMEOUT = timedelta(minutes=3)


def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
    )


def create_session(identity: str) -> str:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    session_id = str(uuid.uuid4())
    now = datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO sessions (session_id, user_email, last_activity, active)
        VALUES (%s, %s, %s, TRUE)
        """,
        (session_id, identity, now)
    )

    db.commit()
    cursor.close()
    db.close()

    return session_id


def validate_session(session_id: str) -> str | None:
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM sessions WHERE session_id=%s AND active=TRUE",
        (session_id,)
    )
    session = cursor.fetchone()

    if not session:
        cursor.close()
        db.close()
        return None

    last_activity = session["last_activity"]

    if datetime.utcnow() - last_activity > SESSION_TIMEOUT:
        cursor.execute(
            "UPDATE sessions SET active=FALSE WHERE session_id=%s",
            (session_id,)
        )
        db.commit()
        cursor.close()
        db.close()
        return None

    # update activity timestamp
    cursor.execute(
        "UPDATE sessions SET last_activity=%s WHERE session_id=%s",
        (datetime.utcnow(), session_id)
    )
    db.commit()

    user_identity = session["user_email"]

    cursor.close()
    db.close()

    return user_identity


def invalidate_session(session_id: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "UPDATE sessions SET active=FALSE WHERE session_id=%s",
        (session_id,)
    )

    db.commit()
    cursor.close()
    db.close()
