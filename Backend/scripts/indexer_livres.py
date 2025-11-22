import os
import sys
import re
import multiprocessing as mp
from tqdm import tqdm
from collections import defaultdict
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from pymongo import UpdateOne

# Accès à la base locale
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db

# Initialisation NLTK
import nltk
try:
    nltk.data.find("corpora/wordnet")
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("wordnet")
    nltk.download("stopwords")

lemmatizer = WordNetLemmatizer()
STOPWORDS = set(stopwords.words("english"))

# 1- Nettoyage et lemmatisation stricte
def nettoyer_et_lemmatiser_fichier(chemin, chunk_size=400_000):
    mots_filtres = []
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Nettoyage : on garde uniquement les lettres
                chunk = re.sub(r"[^a-zA-Z]", " ", chunk).lower()
                mots = re.findall(r"[a-z]{4,15}", chunk)  # entre 4 et 15 caractères

                # Stopwords + lemmatisation
                for m in mots:
                    if m in STOPWORDS:
                        continue
                    lem = lemmatizer.lemmatize(m)
                    mots_filtres.append(lem)
    except Exception as e:
        print(f"⚠️ Erreur lecture {chemin}: {e}")
    return mots_filtres


# 2-Indexation d’un seul livre
def indexer_un_livre(livre):
    chemin = livre.get("chemin")
    if not chemin or not os.path.exists(chemin):
        return None

    mots = nettoyer_et_lemmatiser_fichier(chemin)
    if not mots:
        return None

    freq = {}
    for mot in mots:
        freq[mot] = freq.get(mot, 0) + 1

    # On jette les mots très rares (1 occurrence dans le livre)
    freq = {m: c for m, c in freq.items() if c > 1}
    if not freq:
        return None

    total = sum(freq.values())
    freq_tf = {mot: count / total for mot, count in freq.items()}
    return (livre["gutendexId"], freq_tf)


# 3-Worker parallèle
def worker(livres):
    resultats = []
    for livre in livres:
        res = indexer_un_livre(livre)
        if res:
            resultats.append(res)
    return resultats


# 4- Fusion globale + filtre DF (doc frequency) 
def fusionner_resultats(all_results, tf_global_min=0.001):
    mot_index = {}
    tf_global = defaultdict(float)

    # Construire les fréquences globales
    for book_id, freqs in all_results:
        for mot, tf in freqs.items():
            mot_index.setdefault(mot, {})
            mot_index[mot][str(book_id)] = tf
            tf_global[mot] += tf

    # Filtrage basé sur TF global
    mot_index_filtre = {
        mot: livres for mot, livres in mot_index.items()
        if tf_global[mot] >= tf_global_min
    }

    print(f"📊 Filtrage TF-global : {len(mot_index)} → {len(mot_index_filtre)} mots conservés")
    return mot_index_filtre



# 5- Insertion MongoDB rapide 
def inserer_batch(index_col, mot_index):
    if not mot_index:
        return
    bulk_ops = [
        UpdateOne({"mot": mot}, {"$set": {"livres": livres}}, upsert=True)
        for mot, livres in mot_index.items()
    ]
    index_col.bulk_write(bulk_ops, ordered=False)
    print(f"📤 {len(bulk_ops)} mots insérés dans MongoDB (batch).")


# 6- Fonction principale 
def main(nb_livres=None):
    print("🚀 Démarrage de l'indexation parallèle stricte...")
    db = get_db()
    livres_col = db["livres"]
    index_col = db["index"]

    # Nettoyage de l'ancien index
    index_col.delete_many({})

    # Récupération des livres
    livres = list(livres_col.find())

    # Si un nombre est fourni → on limite
    if nb_livres is not None:
        livres = livres[:nb_livres]

    print(f"📚 {len(livres)} livres utilisés pour ce benchmark.\n")

    nb_process = min(8, mp.cpu_count())
    chunk_size = max(1, len(livres) // nb_process)
    chunks = [livres[i:i + chunk_size] for i in range(0, len(livres), chunk_size)]

    # Étape 1 : calcul parallèle
    all_results = []
    with mp.Pool(processes=nb_process) as pool:
        for res in tqdm(pool.imap(worker, chunks), total=len(chunks), desc="🧠 Traitement parallèle"):
            all_results.extend(res)

    # Étape 2 : fusion globale avec DF 
    mot_index = fusionner_resultats(all_results)

    # Étape 3 : insertion MongoDB par batch
    mots = list(mot_index.items())
    BATCH_SIZE = 5000
    for i in range(0, len(mots), BATCH_SIZE):
        inserer_batch(index_col, dict(mots[i:i+BATCH_SIZE]))

    print(f"✅ Indexation terminée ! {index_col.count_documents({})} mots indexés.")
    close_db()



# === Lancement ===
if __name__ == "__main__":
    main()
