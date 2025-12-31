from fastapi import Form
import time

@app.post("/reveal")
def reveal_file(
    file_id: str = Form(...),
    x_session_id: str = Header(..., alias="X-Session-ID"),
    request: Request = None
):
    # 🔐 Require valid session
    user = require_session(request)

    cursor.execute(
        "SELECT * FROM secure_files WHERE id=%s",
        (file_id,)
    )
    record = cursor.fetchone()

    if not record:
        raise HTTPException(404, "FILE_NOT_FOUND")

    if record["locked"]:
        raise HTTPException(403, "FILE_LOCKED")

    now = int(time.time())

    if now > record["created_at"] + record["expiry_seconds"]:
        raise HTTPException(410, "FILE_EXPIRED")

    if record["views_used"] >= record["max_views"]:
        raise HTTPException(403, "MAX_VIEWS_REACHED")

    # ✅ Increment view count
    cursor.execute(
        "UPDATE secure_files SET views_used = views_used + 1 WHERE id=%s",
        (file_id,)
    )
    db.commit()

    return {
        "status": "ACCESS_GRANTED",
        "file_id": file_id
    }
