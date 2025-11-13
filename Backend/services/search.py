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

    # 1-Récupère toutes les entrées pour tous les keywords
    if search_type == "keyword":
        entries = index_col.find({"mot": {"$in": keywords}})
    else:
        # TEXT SEARCH (beaucoup plus rapide que regex)
        entries = index_col.find({ "$text": { "$search": " ".join(keywords) } })

    # 2-Stocke pour chaque keyword → {keyword: {livre_id: freq}}
    books_per_keyword = {kw: {} for kw in keywords}

    for entry in entries:
        mot = entry["mot"]
        if mot not in books_per_keyword:
            continue

        for lid, occ in entry["livres"].items():
            books_per_keyword[mot][lid] = occ

    # 3-UNION ou INTERSECTION selon présence de "|"
    if "|" in pattern:  # UNION
        combined_books = {}
        for d in books_per_keyword.values():
            for lid, occ in d.items():
                combined_books[lid] = combined_books.get(lid, 0) + occ

    else:  # INTERSECTION (AND)
        # Prendre les livres présents dans tous les dicos
        all_sets = [set(d.keys()) for d in books_per_keyword.values()]
        intersection_ids = set.intersection(*all_sets) if all_sets else set()

        combined_books = {
            lid: sum(d.get(lid, 0) for d in books_per_keyword.values())
            for lid in intersection_ids
        }

    if not combined_books:
        return []

    # 4-Charger les infos Mongo en UNE SEULE FOIS
    livre_ids = [int(l) for l in combined_books.keys()]

    livres = {
        str(doc["gutendexId"]): doc
        for doc in livres_col.find({"gutendexId": {"$in": livre_ids}}, {"_id": 0})
    }

    centralites = {
        doc["livreId"]: doc["scoreGlobal"]
        for doc in centr_col.find({"livreId": {"$in": [str(l) for l in livre_ids]}}, {"_id": 0})
    }

    # 5-Construction finale
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

    # 6-Tri final ultra rapide
    return sorted(resultats, key=lambda x: x["scoreGlobal"], reverse=True)[:20]

def search_regex_in_index(regex_pattern: str):
    try:
        reg = re.compile(regex_pattern)
    except:
        return []  # mauvaise regex

    matching_entries = index_col.find({
        "mot": {"$regex": regex_pattern}
    })

    combined_books = {}

    for entry in matching_entries:
        for lid, occ in entry["livres"].items():
            combined_books[lid] = combined_books.get(lid, 0) + occ

    return combined_books

def format_results(combined_books):
    """
    combined_books = { livre_id: fréquence }
    Formate les résultats en ajoutant :
    - titre, auteur, coverUrl, downloadCount
    - scoreGlobal
    - tri final
    """
    if not combined_books:
        return []

    # Charger les infos Mongo en UNE fois
    livre_ids = [int(l) for l in combined_books.keys()]

    # Infos livres
    livres = {
        str(doc["gutendexId"]): doc
        for doc in livres_col.find(
            {"gutendexId": {"$in": livre_ids}},
            {"_id": 0}
        )
    }

    # Infos centralité
    centralites = {
        doc["livreId"]: doc.get("scoreGlobal", 0)
        for doc in centr_col.find(
            {"livreId": {"$in": [str(l) for l in livre_ids]}},
            {"_id": 0}
        )
    }

    # Construire résultats
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
                        "auteur": livre.get("auteur", "Inconnu"),
                        "coverUrl": livre.get("coverUrl", ""),
                        "downloadCount": livre.get("downloadCount", 0)
                    })

        except Exception as e:
            print(f"⚠️ Erreur lecture {chemin}: {e}")
            continue

    return resultats


# 5- Fonction principale
def search(pattern: str, search_type: str = "keyword"):
    if search_type == "keyword":
        return search_in_index(pattern)

    elif search_type == "regex":
        # 1) REGEX SUR L'INDEX (rapide)
        result_index = search_regex_in_index(pattern)
        if result_index:
            return format_results(result_index)

        # 2) REGEX SUR LES FICHIERS (lent)
        return search_in_files(pattern)

    elif search_type == "kmp":
        return search_in_files(pattern, "kmp")

    else:
        raise ValueError(f"Type non supporté : {search_type}")

