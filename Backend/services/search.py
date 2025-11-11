import re
import os
from services.kmp import kmp_search
from database import get_db

# --- Connexion MongoDB ---
db = get_db()
index_col = db["index"]
livres_col = db["livres"]
centr_col = db["centrality"] 


# 1- Découper la requête utilisateur
def split_pattern(pattern: str, search_type: str):
    """Découpe le texte de recherche en mots-clés (sauf en mode regex)."""
    if search_type == "regex":
        return [pattern]
    return [w.lower() for w in re.split(r"[^\w]+", pattern) if len(w) > 3]


# 2- Comparaison de mots
def is_keyword_match(index_word: str, keyword: str, search_type: str) -> bool:
    if search_type == "keyword":
        return index_word == keyword
    return keyword in index_word


# 3- Recherche par mot-clé avec tri par scoreGlobal
def search_in_index(pattern: str, search_type: str = "keyword"):
    keywords = split_pattern(pattern, search_type)
    if not keywords:
        return []

    book_maps = []

    for keyword in keywords:
        matching_books = {}

        if search_type == "keyword":
            entries = index_col.find({"mot": keyword})
        else:
            entries = index_col.find({"mot": {"$regex": keyword}})

        for entry in entries:
            for livre_id, occ in entry["livres"].items():
                matching_books[livre_id] = matching_books.get(livre_id, 0) + occ

        book_maps.append(matching_books)

    # Union / intersection
    if "|" in pattern:
        combined_books = {}
        for m in book_maps:
            for lid, occ in m.items():
                combined_books[lid] = combined_books.get(lid, 0) + occ
    else:
        combined_books = book_maps[0]
        for m in book_maps[1:]:
            combined_books = {
                lid: combined_books[lid] + m[lid]
                for lid in combined_books if lid in m
            }

    resultats = []

    # Tri par scoreGlobal uniquement
    for livre_id, freq in combined_books.items():
        livre = livres_col.find_one(
            {"gutendexId": int(livre_id)},
            {"_id": 0, "titre": 1, "auteur": 1}
        )
        centralite = centr_col.find_one(
            {"livreId": str(livre_id)},
            {"_id": 0, "scoreGlobal": 1}
        )
        score = centralite["scoreGlobal"] if centralite else 0

        if livre:
            resultats.append({
                "livreId": livre_id,
                "titre": livre["titre"],
                "auteur": livre.get("auteur", "Inconnu"),
                "frequence": freq,
                "scoreGlobal": score
            })

    # Tri final uniquement selon le scoreGlobal décroissant
    resultats = sorted(resultats, key=lambda x: x["scoreGlobal"], reverse=True)

    return resultats[:20]  # top 20 meilleurs livres


# 4 - Recherche Regex ou KMP inchangée
def search_in_files(pattern: str, search_type: str):
    resultats = []
    livres = list(livres_col.find())

    for livre in livres:
        chemin = livre.get("chemin")
        if not chemin or not os.path.exists(chemin):
            continue

        try:
            with open(chemin, "r", encoding="utf-8") as f:
                contenu = f.read().lower()
                trouve = False

                if search_type == "regex":
                    trouve = bool(re.search(pattern, contenu))
                elif search_type == "kmp":
                    trouve = bool(kmp_search(contenu, pattern.lower()))

                if trouve:
                    resultats.append({
                        "livreId": livre["gutendexId"],
                        "titre": livre["titre"],
                        "auteur": livre.get("auteur", "Inconnu")
                    })

        except Exception as e:
            print(f"⚠️ Erreur lecture {chemin}: {e}")
            continue

    return resultats


# 5- Fonction principale
def search(pattern: str, search_type: str = "keyword"):
    if search_type == "keyword":
        return search_in_index(pattern, search_type)
    elif search_type in ["regex", "kmp"]:
        return search_in_files(pattern, search_type)
    else:
        raise ValueError(f"Type de recherche non supporté : {search_type}")
