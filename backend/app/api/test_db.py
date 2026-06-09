from fastapi import APIRouter
from app.db.mongo import db

router = APIRouter()

@router.get("/test-db")
def test_db():
    try:
        db.list_collection_names()
        return {"status": "MongoDB connected successfully 🚀"}
    except Exception as e:
        return {"error": str(e)}
