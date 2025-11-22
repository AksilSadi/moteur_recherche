import os
import json
import re
from database import get_db
from services.trie import Trie
from nltk.stem import PorterStemmer

ps = PorterStemmer()

WORD_REGEX = re.compile(r"[a-zA-Z]{3,20}")
TRIE_FILE = "trie.json"


def extract_words(text):
    return WORD_REGEX.findall(text.lower())


def build_trie_filtered_by_index(nb_livres=None):
    """
    Construit un TRIE à partir de nb_livres livres (pour les benchmarks).
    Si nb_livres=None → utilise tous les livres.
    """
    db = get_db()
    index_col = db["index"]

    # Charger TOUS les stems valides depuis l'index des mots
    valid_stems = set(index_col.distinct("mot"))

    # Charger livres
    livres_cursor = db["livres"].find()
    if nb_livres is not None:
        livres_cursor = livres_cursor.limit(nb_livres)

    trie = Trie()
    word_popularity = {}

    print(f"📚 Construction TRIE à partir de {nb_livres or 'TOUS'} livres...")

    for livre in livres_cursor:
        chemin = livre.get("chemin")
        if not chemin or not os.path.exists(chemin):
            continue

        try:
            with open(chemin, "r", encoding="utf-8") as f:
                txt = f.read()
        except:
            continue

        words = set(extract_words(txt))

        for w in words:
            stem = ps.stem(w)
            if stem not in valid_stems:
                continue

            word_popularity[w] = word_popularity.get(w, 0) + 1

    # Remplissage du TRIE
    for word, score in word_popularity.items():
        trie.insert(word, score)

    print(f"✅ TRIE construit avec {len(word_popularity)} mots.")
    return trie



def load_or_build_trie():
    if os.path.exists(TRIE_FILE):
        print("⚡ Chargement du TRIE depuis trie.json...")
        with open(TRIE_FILE, "r", encoding="utf-8") as f:
            return Trie.from_dict(json.load(f))

    trie = build_trie_filtered_by_index()

    print("💾 Sauvegarde du TRIE dans trie.json...")
    with open(TRIE_FILE, "w", encoding="utf-8") as f:
        json.dump(trie.to_dict(), f)

    return trie


TRIE_INSTANCE = load_or_build_trie()
