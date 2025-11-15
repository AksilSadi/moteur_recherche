import re
import os
from database import get_db
from nltk.stem import PorterStemmer

# --- Initialisation du stemmer ---
stemmer = PorterStemmer()

# --- Connexion MongoDB ---
db = get_db()
index_col = db["index"]
livres_col = db["livres"]
centr_col = db["centrality"]


# 1-Découpe + Stemming
def split_pattern(pattern: str, search_type: str):
    """Découpe la requête et renvoie les STEMS pour cohérence avec autocomplétion"""
    if search_type == "regex":
        return [stemmer.stem(pattern.lower())]

    words = [w.lower() for w in re.split(r"[^\w]+", pattern) if len(w) > 2]
    stems = [stemmer.stem(w) for w in words]
    return stems


# 2- Recherche dans l’INDEX MongoDB
def search_in_index(pattern: str, search_type: str = "keyword"):
    stems = split_pattern(pattern, search_type)
    if not stems:
        return []

    # Recherche directe via index (super rapide)
    if search_type == "keyword":
        entries = index_col.find({"mot": {"$in": stems}})
    else:
        # Full text search basé sur les stems
        entries = index_col.find({"$text": {"$search": " ".join(stems)}})

    books_per_stem = {stem: {} for stem in stems}

    for entry in entries:
        mot = entry["mot"]
        if mot not in books_per_stem:
            continue
        for lid, occ in entry["livres"].items():
            books_per_stem[mot][lid] = occ

    # UNION si | présent
    if "|" in pattern:
        combined_books = {}
        for d in books_per_stem.values():
            for lid, occ in d.items():
                combined_books[lid] = combined_books.get(lid, 0) + occ

    # Sinon INTERSECTION
    else:
        sets = [set(d.keys()) for d in books_per_stem.values()]
        intersection = set.intersection(*sets) if sets else set()

        combined_books = {
            lid: sum(d.get(lid, 0) for d in books_per_stem.values())
            for lid in intersection
        }

    return format_results(combined_books)


# 3-REGEX rapide via INDEX
def search_regex_in_index(regex_pattern: str):
    """Regex appliqué au STEM uniquement pour cohérence avec autocomplétion"""
    try:
        reg = re.compile(regex_pattern)
    except:
        return {}

    matching_entries = index_col.find({"mot": {"$regex": regex_pattern}})
    combined_books = {}

    for entry in matching_entries:
        for lid, occ in entry["livres"].items():
            combined_books[lid] = combined_books.get(lid, 0) + occ

    return combined_books


# 4- Formatage final + chargements groupés
def format_results(combined_books):
    if not combined_books:
        return []

    livre_ids = [int(l) for l in combined_books.keys()]

    # Charger livres d'un coup
    livres = {
        str(doc["gutendexId"]): doc
        for doc in livres_col.find(
            {"gutendexId": {"$in": livre_ids}}, {"_id": 0}
        )
    }

    # Charger centralités d'un coup
    centralites = {
        doc["livreId"]: doc.get("scoreGlobal", 0)
        for doc in centr_col.find(
            {"livreId": {"$in": [str(l) for l in livre_ids]}}
        )
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
            "scoreGlobal": centralites.get(str(lid), 0),
        })

    # Tri final : scoreGlobal
    return sorted(resultats, key=lambda x: x["scoreGlobal"], reverse=True)[:20]


# 5-REGEX lente (fichiers) uniquement en fallback
def search_in_files(regex_pattern: str):
    resultats = []
    livres = list(livres_col.find())

    try:
        reg = re.compile(regex_pattern)
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
                        "downloadCount": livre.get("downloadCount", 0),
                    })
        except:
            continue

    return resultats


# 6- Fonction principale
def search(pattern: str, search_type: str = "keyword"):

    # 🔍 RECHERCHE MOT-CLÉ (stem-based)
    if search_type == "keyword":
        return search_in_index(pattern)

    # 🔍 RECHERCHE REGEX
    elif search_type == "regex":
        stem = stemmer.stem(pattern.lower())

        # 1) regex rapide via index
        index_matches = search_regex_in_index(stem)
        if index_matches:
            return format_results(index_matches)

        # 2) fallback REGEX sur fichiers
        return search_in_files(stem)

    else:
        raise ValueError(f"Type non supporté : {search_type}")
