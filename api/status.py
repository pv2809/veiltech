from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/status/{file_id}")
def file_status(file_id: str):
    cursor.execute("SELECT * FROM secure_files WHERE id=%s", (file_id,))
    record = cursor.fetchone()

    if not record:
        raise HTTPException(404, "NOT_FOUND")

    return {
        "views_used": record["views_used"],
        "max_views": record["max_views"],
        "failed_attempts": record["failed_attempts"],
        "locked": record["locked"]
    }
