import os
import json
import re
from database import get_db
from services.trie import Trie

WORD_REGEX = re.compile(r"[a-zA-Z]{3,12}")
TRIE_FILE = "trie.json"

def extract_words(text):
    return WORD_REGEX.findall(text.lower())


def build_trie_from_books():
    db = get_db()
    livres = db["livres"].find()

    trie = Trie()
    word_popularity = {}

    print("📚 Construction du TRIE à partir des fichiers...")

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
            word_popularity[w] = word_popularity.get(w, 0) + 1

    # Remplir le trie
    for word, score in word_popularity.items():
        trie.insert(word, score)

    print(f"✅ TRIE construit avec {len(word_popularity)} mots.")

    return trie


def load_or_build_trie():
    # 1. Charger si déjà existant
    if os.path.exists(TRIE_FILE):
        print("⚡ Chargement du TRIE depuis trie.json...")
        with open(TRIE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Trie.from_dict(data)

    # 2. Sinon : construire et sauvegarder
    trie = build_trie_from_books()

    print("💾 Sauvegarde du TRIE dans trie.json...")
    with open(TRIE_FILE, "w", encoding="utf-8") as f:
        json.dump(trie.to_dict(), f)

    return trie


TRIE_INSTANCE = load_or_build_trie()
