from fastapi import APIRouter, Query
from database import get_db

router = APIRouter(prefix="/livres", tags=["Livres"])
db = get_db()

# 1. Liste des livres
@router.get("/")
def get_livres(limit: int = 10):
    livres = list(db["livres"].find().limit(limit))
    for l in livres:
        l["_id"] = str(l["_id"])
    return {"total": len(livres), "livres": livres}
