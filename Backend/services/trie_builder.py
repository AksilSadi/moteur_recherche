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


def build_trie_filtered_by_index():
    """
    Construit un TRIE :
    - basé sur les mots réels des fichiers
    - mais ne garde que ceux dont le STEM existe dans l’index MongoDB
    """
    db = get_db()
    index_col = db["index"]
    livres = db["livres"].find()

    # Charger TOUS les stems valides depuis MongoDB
    valid_stems = set(index_col.distinct("mot"))  # ex: {"love", "time", "book"...}

    trie = Trie()
    word_popularity = {}

    print("📚 Construction TRIE filtré par index...")

    for livre in livres:
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

            # ⚠️ Garder seulement les mots dont la racine existe dans l'index
            if stem not in valid_stems:
                continue

            # enregistrer popularité (nb livres contenant ce mot)
            word_popularity[w] = word_popularity.get(w, 0) + 1

    # Remplir le TRIE
    for word, score in word_popularity.items():
        trie.insert(word, score)

    print(f"✅ TRIE construit avec {len(word_popularity)} mots valides.")
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
