import re
import os
from database import get_db

# --- Connexion MongoDB ---
db = get_db()
index_col = db["index"]
livres_col = db["livres"]
centr_col = db["centrality"]


# --------------------------------------------------------
# 1) Découper la requête utilisateur
# --------------------------------------------------------
def split_pattern(pattern: str, search_type: str):
    if search_type == "regex":
        return [pattern]
    return [w.lower() for w in re.split(r"[^\w]+", pattern) if len(w) > 3]


# --------------------------------------------------------
# 2) Recherche par mot-clé via INDEX MongoDB
# --------------------------------------------------------
def search_in_index(pattern: str, search_type="keyword"):
    keywords = split_pattern(pattern, search_type)
    if not keywords:
        return []

    # Keyword search
    if search_type == "keyword":
        entries = index_col.find({"mot": {"$in": keywords}})
    else:
        # Full text search (Mongo TEXT index)
        entries = index_col.find({"$text": {"$search": " ".join(keywords)}})

    books_per_keyword = {kw: {} for kw in keywords}

    for entry in entries:
        mot = entry["mot"]

        if mot not in books_per_keyword:
            continue

        for lid, occ in entry["livres"].items():
            books_per_keyword[mot][lid] = occ

    # UNION si pattern contient "|", sinon INTERSECTION
    if "|" in pattern:
        combined_books = {}
        for d in books_per_keyword.values():
            for lid, occ in d.items():
                combined_books[lid] = combined_books.get(lid, 0) + occ

    else:
        # intersection
        all_sets = [set(d.keys()) for d in books_per_keyword.values()]
        intersection_ids = set.intersection(*all_sets) if all_sets else set()

        combined_books = {
            lid: sum(d.get(lid, 0) for d in books_per_keyword.values())
            for lid in intersection_ids
        }

    return format_results(combined_books)


# --------------------------------------------------------
# 3) Regex sur INDEX MongoDB
# --------------------------------------------------------
def search_regex_in_index(regex_pattern: str):
    try:
        re.compile(regex_pattern)
    except:
        return {}

    matching_entries = index_col.find({"mot": {"$regex": regex_pattern}})

    combined_books = {}
    for entry in matching_entries:
        for lid, occ in entry["livres"].items():
            combined_books[lid] = combined_books.get(lid, 0) + occ

    return combined_books


# --------------------------------------------------------
# 4) Formatage final + chargement MongoDB
# --------------------------------------------------------
def format_results(combined_books):
    if not combined_books:
        return []

    livre_ids = [int(l) for l in combined_books.keys()]

    # Charger les livres d’un coup
    livres = {
        str(doc["gutendexId"]): doc
        for doc in livres_col.find({"gutendexId": {"$in": livre_ids}}, {"_id": 0})
    }

    # Charger centralité d’un coup
    centralites = {
        doc["livreId"]: doc.get("scoreGlobal", 0)
        for doc in centr_col.find({"livreId": {"$in": [str(l) for l in livre_ids]}}, {"_id": 0})
    }

    resultats = []
    for lid, freq in combined_books.items():
        livre = livres.get(str(lid))
        if not livre:
            continue

        resultats.append({
            "livreId": lid,
            "titre": livre["titre"],
            "auteur": livre.get("auteur", "Inconnu"),
            "coverUrl": livre.get("coverUrl", ""),
            "downloadCount": livre.get("downloadCount", 0),
            "frequence": freq,
            "scoreGlobal": centralites.get(str(lid), 0)
        })

    # Tri final
    return sorted(resultats, key=lambda x: x["scoreGlobal"], reverse=True)[:20]


# --------------------------------------------------------
# 5) Recherche REGEX sur les fichiers (fallback lent)
# --------------------------------------------------------
def search_in_files(pattern: str):
    resultats = []
    livres = list(livres_col.find())

    try:
        reg = re.compile(pattern)
    except:
        return []

    for livre in livres:
        chemin = livre.get("chemin")
        if not chemin or not os.path.exists(chemin):
            continue

        try:
            with open(chemin, "r", encoding="utf-8") as f:
                contenu = f.read().lower()
                if reg.search(contenu):
                    resultats.append({
                        "livreId": livre["gutendexId"],
                        "titre": livre["titre"],
                        "auteur": livre.get("auteur", "Inconnu"),
                        "coverUrl": livre.get("coverUrl", ""),
                        "downloadCount": livre.get("downloadCount", 0)
                    })

        except Exception as e:
            print(f"⚠️ Erreur lecture {chemin}: {e}")

    return resultats


# --------------------------------------------------------
# 6) Fonction principale
# --------------------------------------------------------
def search(pattern: str, search_type: str = "keyword"):
    # --- Recherche par mot-clé ---
    if search_type == "keyword":
        return search_in_index(pattern)

    # --- Recherche par RegEx ---
    elif search_type == "regex":
        # 1) Test rapide via INDEX
        index_matches = search_regex_in_index(pattern)
        if index_matches:
            return format_results(index_matches)

        # 2) Sinon recherche lente dans les fichiers
        return search_in_files(pattern)

    else:
        raise ValueError(f"Type non supporté : {search_type}")
