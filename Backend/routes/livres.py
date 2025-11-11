from fastapi import APIRouter, Query
from database import get_db
from services.search import search

router = APIRouter(prefix="/livres", tags=["Livres"])
db = get_db()

# 1. Liste des livres
@router.get("/")
def get_livres(limit: int = 10):
    livres = list(db["livres"].find().limit(limit))
    for l in livres:
        l["_id"] = str(l["_id"])
    return {"total": len(livres), "livres": livres}

@router.get("/search")
def rechercher(
    q: str = Query(..., min_length=2),
    type: str = Query("keyword", enum=["keyword", "regex", "kmp"])
):
    resultats = search(q, type)
    return {"query": q, "type": type, "resultats": resultats}