import re
import os
from KMP import kmp_search
from database import get_db
# --- Connexion MongoDB ---
db=get_db()
index_col = db["index"]
livres_col = db["livres"]

# 1-découper la requête utilisateur
def split_pattern(pattern: str, search_type: str):
    """Découpe le texte de recherche en mots-clés (sauf en mode regex)."""
    if search_type == "regex":
        return [pattern]
    return [w.lower() for w in re.split(r"[^\w]+", pattern) if len(w) > 3]


# 2-comparer les mots d'index
def is_keyword_match(index_word: str, keyword: str, search_type: str) -> bool:
    """Retourne True si le mot de l’index correspond au mot recherché."""
    if search_type == "keyword":
        return index_word == keyword
    return keyword in index_word


# 3- Recherche par mot-clé (avec union/intersection)
def search_in_index(pattern: str, search_type: str = "keyword"):
    """
    Recherche dans la collection 'index' :
    - Si l'utilisateur tape plusieurs mots séparés par un espace → intersection
    - S'il met un | (OR logique) → union
    """
    keywords = split_pattern(pattern, search_type)
    if not keywords:
        return []

    # 🔹 Liste des dictionnaires {livre_id: occurrence}
    book_maps = []

    for keyword in keywords:
        matching_books = {}
        for entry in index_col.find():
            mot = entry["mot"]
            if is_keyword_match(mot, keyword, search_type):
                for livre_id, occ in entry["livres"].items():
                    matching_books[livre_id] = matching_books.get(livre_id, 0) + occ
        book_maps.append(matching_books)

    # 🔹 Combinaison : intersection ou union
    if "|" in pattern:  # union
        combined_books = {}
        for m in book_maps:
            for lid, occ in m.items():
                combined_books[lid] = combined_books.get(lid, 0) + occ
    else:  # intersection
        combined_books = book_maps[0]
        for m in book_maps[1:]:
            combined_books = {lid: combined_books[lid] + m[lid]
                              for lid in combined_books if lid in m}

    # 🔹 Trie par fréquence décroissante
    sorted_books = sorted(combined_books.items(), key=lambda x: x[1], reverse=True)

    # 🔹 Enrichir avec les métadonnées de la collection "livres"
    resultats = []
    for livre_id, freq in sorted_books:
        livre = livres_col.find_one({"gutendexId": int(livre_id)})
        if livre:
            resultats.append({
                "livreId": livre_id,
                "titre": livre.get("titre", "Inconnu"),
                "auteur": livre.get("auteur", "Inconnu"),
                "frequence": freq
            })

    return resultats


# 4- Recherche Regex ou KMP dans les fichiers
def search_in_files(pattern: str, search_type: str):
    """Recherche avancée dans les fichiers (Regex ou KMP)."""
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


# 5-Fonction principale unifiée
def search(pattern: str, search_type: str = "keyword"):
    """
    Recherche principale :
    - keyword → dans MongoDB (index)
    - regex / kmp → dans les fichiers
    """
    if search_type == "keyword":
        return search_in_index(pattern, search_type)
    elif search_type in ["regex", "kmp"]:
        return search_in_files(pattern, search_type)
    else:
        raise ValueError(f"Type de recherche non supporté : {search_type}")
