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
    type: str = Query("keyword", enum=["keyword", "regex"]),
    page: int = Query(1, ge=1),
    limit: int = Query(8, ge=1, le=50)
):

    # Tous les résultats triés par scoreGlobal
    tous_les_resultats = search(q, type)

    total = len(tous_les_resultats)

    # Top 3 global pour suggestions
    top3 = tous_les_resultats[:3]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    page_items = tous_les_resultats[start:end]

    return {
        "query": q,
        "type": type,
        "page": page,
        "limit": limit,
        "total": total,
        "resultats": page_items,
        "top3": top3
    }



# 2. Détails d’un livre par son ID
@router.get("/id/{livre_id}")
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

    # 1) Charger toutes les similarités d’un coup
    docs = list(similarity_col.find({
        "$or": [{"livre1": livre_id}, {"livre2": livre_id}]
    }))

    if not docs:
        return {"error": "Aucune similarité trouvée pour ce livre"}

    # 2) Extraire tous les other_id
    other_ids = [
        d["livre2"] if d["livre1"] == livre_id else d["livre1"]
        for d in docs
    ]

    # 3) Charger TOUS les livres en 1 requête
    livres = {
        str(doc["gutendexId"]): doc
        for doc in livres_col.find(
            {"gutendexId": {"$in": [int(x) for x in other_ids]}},
            {"_id": 0}
        )
    }

    # 4) Charger TOUTES les centralités en 1 requête
    centralites = {
        doc["livreId"]: doc.get("scoreGlobal", 0)
        for doc in centr_col.find(
            {"livreId": {"$in": other_ids}},
            {"_id": 0}
        )
    }

    # 5) Construction directe des recommandations
    recommandations = []
    for d, other_id in zip(docs, other_ids):
        livre = livres.get(str(other_id))
        if not livre:
            continue

        recommandations.append({
            "gutendexId": other_id,
            "titre": livre["titre"],
            "auteur": livre.get("auteur", "Inconnu"),
            "downloadCount": livre.get("downloadCount", 0),
            "coverUrl": livre.get("coverUrl", None),
            "birthYear": livre.get("birthYear", None),
            "deathYear": livre.get("deathYear", None),
            "subjects": livre.get("subjects", []),
            "languages": livre.get("languages", []),
            "rights": livre.get("rights", None),
            "bookshelves": livre.get("bookshelves", []),
            "mediaType": livre.get("mediaType", None),
            "gutenbergUrl": livre.get("gutenbergUrl", None),
            "similarite": d.get("jaccard", 0),
            "scoreGlobal": centralites.get(other_id, 0)
        })

    # 6) Trier
    recommandations.sort(key=lambda x: (x["similarite"], x["scoreGlobal"]), reverse=True)

    # 7) Retourner les 8 meilleurs
    return {
        "livre_id": livre_id,
        "recommendations": recommandations[:8]
    }

@router.get("/autocomplete")
def autocomplete(prefix: str):
    if not prefix or len(prefix) < 2:
        return []

    return TRIE_INSTANCE.autocomplete(prefix.lower())