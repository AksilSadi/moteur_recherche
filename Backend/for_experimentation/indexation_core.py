# indexation_core.py
import os
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import defaultdict

lemmatizer = WordNetLemmatizer()
STOPWORDS = set(stopwords.words("english"))

def nettoyer_et_lemmatiser_fichier(chemin, chunk_size=400_000):
    mots_filtres = []
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                chunk = re.sub(r"[^a-zA-Z]", " ", chunk).lower()
                mots = re.findall(r"[a-z]{4,15}", chunk)

                for m in mots:
                    if m in STOPWORDS:
                        continue
                    mots_filtres.append(lemmatizer.lemmatize(m))
    except:
        pass

    return mots_filtres


def indexer_un_livre_local(livre):
    chemin = livre.get("chemin")
    if not chemin or not os.path.exists(chemin):
        return None

    mots = nettoyer_et_lemmatiser_fichier(chemin)
    if not mots:
        return None

    freq = {}
    for m in mots:
        freq[m] = freq.get(m, 0) + 1

    # filtre local
    freq = {m: c for m, c in freq.items() if c > 1}
    if not freq:
        return None

    total = sum(freq.values())
    freq_tf = {mot: count / total for mot, count in freq.items()}
    return livre["gutendexId"], freq_tf


def fusionner_local(all_results, tf_global_min=0.001):
    mot_index = {}
    tf_global = defaultdict(float)

    for book_id, freqs in all_results:
        for mot, tf in freqs.items():
            mot_index.setdefault(mot, {})
            mot_index[mot][str(book_id)] = tf
            tf_global[mot] += tf

    mot_index_filtre = {
        mot: livres
        for mot, livres in mot_index.items()
        if tf_global[mot] >= tf_global_min
    }

    return mot_index_filtre
