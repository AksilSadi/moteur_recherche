from fastapi import APIRouter, Query
from database import get_db
from services.search import search
from services.trie_builder import load_or_build_trie

TRIE_INSTANCE = load_or_build_trie()

router = APIRouter(prefix="/livres", tags=["Livres"])
db = get_db()

# 1. Liste des livres
@router.get("/")
def get_livres(
    page: int = Query(1, ge=1, description="Numéro de la page (>= 1)"),
    limit: int = Query(9, ge=1, le=100, description="Nombre de livres par page (max 100)"),
):
    """
    Récupère une page de livres avec pagination.
    Exemple : /livres/?page=2&limit=9
    """
    skip = (page - 1) * limit  # Nombre de livres à ignorer
    livres_col = db["livres"]

    total_livres = livres_col.count_documents({})  # total pour pagination
    livres = list(livres_col.find().skip(skip).limit(limit))

    # Convertir l’_id en string pour le JSON
    for l in livres:
        l["_id"] = str(l["_id"])

    return {
        "page": page,
        "limit": limit,
        "total": total_livres,
        "total_pages": (total_livres + limit - 1) // limit,
        "livres": livres,
    }

@router.get("/search")
def rechercher(
    q: str = Query(..., min_length=2),
    type: str = Query("keyword", enum=["keyword", "regex", "kmp"])
):
    resultats = search(q, type)
    return {"query": q, "type": type, "resultats": resultats}

# 2. Détails d’un livre par son ID
@router.get("/{livre_id}")
def get_livre(livre_id: str):
    """
    Récupère les détails d’un livre par son ID.
    Exemple : /livres/60d5f4832f8fb814c8d6f1a3
    """
    livres_col = db["livres"]
    livre = livres_col.find_one({"_id": livre_id})

    if not livre:
        return {"error": "Livre non trouvé"}

    # Convertir l’_id en string pour le JSON
    livre["_id"] = str(livre["_id"])
    return livre
# 3- recommandations de livres similaires
@router.get("/{livre_id}/recommendations")
def get_recommendations(livre_id: str):
    similarity_col = db["similarity"]
    livres_col = db["livres"]
    centr_col = db["centrality"]

    # Chercher toutes les similarités qui impliquent ce livre
    docs = list(similarity_col.find({
        "$or": [{"livre1": livre_id}, {"livre2": livre_id}]
    }))

    if not docs:
        return {"error": "Aucune similarité trouvée pour ce livre"}

    recommandations = []

    for d in docs:
        # Trouver l'autre livre dans la paire
        other_id = d["livre2"] if d["livre1"] == livre_id else d["livre1"]
        sim = d.get("jaccard", 0)

        # Récupération du score global
        centrality = centr_col.find_one({"livreId": str(other_id)}, {"scoreGlobal": 1})
        scoreGlobal = centrality["scoreGlobal"] if centrality else 0

        # Récupération du livre
        livre = livres_col.find_one({"gutendexId": int(other_id)}, {"_id": 0})
        if livre:
            recommandations.append({
                "livreId": other_id,
                "titre": livre["titre"],
                "auteur": livre.get("auteur", "Inconnu"),
                "image": livre.get("coverUrl", None),
                "similarite": sim,
                "scoreGlobal": scoreGlobal
            })

    # Trier : 1) similarité, 2) scoreGlobal
    recommandations = sorted(
        recommandations,
        key=lambda x: (x["similarite"], x["scoreGlobal"]),
        reverse=True
    )

    # Garder les 5 meilleurs
    recommandations = recommandations[:5]

    return {
        "livre_id": livre_id,
        "recommendations": recommandations
    }
@router.get("/autocomplete")
def autocomplete(prefix: str):
    if not prefix or len(prefix) < 2:
        return []

    return TRIE_INSTANCE.autocomplete(prefix.lower())