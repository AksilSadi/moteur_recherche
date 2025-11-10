import os
import re
from pymongo import MongoClient
from tqdm import tqdm
import spacy

# 1-Chargement du modèle spaCy (anglais)
print("📘 Chargement du modèle spaCy...")
nlp = spacy.load("en_core_news_md")
print("✅ Modèle spaCy chargé avec succès !")

# 2-Définition des stopwords (français + anglais)
STOPWORDS_FR = {
    "le", "la", "les", "un", "une", "des", "du", "de", "dans", "au", "aux",
    "et", "ou", "mais", "donc", "car", "que", "qui", "quoi", "dont", "où",
    "en", "à", "avec", "pour", "par", "sur", "sous", "ce", "cet", "cette",
    "son", "sa", "ses", "leurs", "leur", "nos", "notre", "votre", "vos",
    "il", "elle", "on", "nous", "vous", "ils", "elles", "ne", "pas", "plus",
    "comme", "si", "y", "se", "me", "te", "toi", "moi", "ma", "mon", "mes",
    "tout", "tous", "toute", "toutes", "afin", "d", "l", "n", "s"
}

STOPWORDS_EN = {
    "the", "and", "is", "in", "to", "of", "a", "that", "it", "on", "for",
    "with", "as", "was", "at", "by", "an", "be", "this", "from", "or",
    "but", "not", "are", "have", "has", "they", "you", "we", "his", "her",
    "its", "my", "your", "their", "all", "any", "so", "if"
}

# 3- Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["bibliotheque"]
livres_col = db["livres"]
index_col = db["index"]
dossier_livres = "livres"

# 4- Nettoyage et lemmatisation du texte
def nettoyer_et_splitter(texte):
    """
    Nettoie et lemmatise un texte :
    - retire la ponctuation et caractères spéciaux
    - passe en minuscules
    - supprime les stopwords
    - renvoie les lemmes des mots significatifs
    """
    # Garder uniquement lettres (français et anglais)
    texte = re.sub(r"[^a-zA-ZàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]", " ", texte)
    texte = texte.lower()

    doc = nlp(texte)
    mots_filtres = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha
        and len(token.lemma_) > 2
        and token.lemma_.lower() not in STOPWORDS_FR
        and token.lemma_.lower() not in STOPWORDS_EN
        and not token.is_stop
    ]
    return mots_filtres

# 5- Indexation d’un seul livre (avec fréquence TF)
def indexer_un_livre(livre):
    chemin = livre.get("chemin")
    if not chemin or not os.path.exists(chemin):
        print(f"⚠️ Fichier introuvable pour {livre.get('titre', 'Inconnu')}")
        return {}

    with open(chemin, "r", encoding="utf-8") as f:
        texte = f.read()

    mots = nettoyer_et_splitter(texte)
    if not mots:
        return {}

    # Comptage des occurrences
    freq = {}
    for mot in mots:
        freq[mot] = freq.get(mot, 0) + 1

    # Normalisation : fréquence (TF)
    total_mots = sum(freq.values())
    freq_tf = {mot: count / total_mots for mot, count in freq.items()}

    return freq_tf

# 6- Fonction principale d’indexation (avec bulk insertion)
def main():
    print("🚀 Début de l'indexation améliorée (lemmatisation + fréquence TF + batch Mongo)...")

    # Réinitialiser l'index
    index_col.delete_many({})
    print("🗑️ Ancien index supprimé.")

    livres = list(livres_col.find())
    print(f"📚 {len(livres)} livres à indexer.\n")

    mot_index = {}  # mémoire temporaire pour stocker les mots avant insertion
    batch_taille = 5000  # nombre de mots avant chaque envoi dans Mongo

    for livre in tqdm(livres, desc="Indexation des livres"):
        try:
            freq_tf = indexer_un_livre(livre)
            for mot, tf in freq_tf.items():
                if mot not in mot_index:
                    mot_index[mot] = {}
                mot_index[mot][str(livre["gutendexId"])] = tf

            # Envoi en base par lot
            if len(mot_index) >= batch_taille:
                inserer_batch(mot_index)
                mot_index = {}

        except Exception as e:
            print(f"❌ Erreur sur le livre {livre.get('titre', 'Inconnu')} : {e}")

    # Dernier batch
    if mot_index:
        inserer_batch(mot_index)

    print(f"✅ Indexation terminée ! {index_col.count_documents({})} mots indexés.")
    client.close()
    print("🔒 Connexion MongoDB fermée.")

# 7- Fonction d’insertion par lot (bulk)
def inserer_batch(mot_index):
    """
    Insère un lot de mots dans MongoDB avec bulk_write (beaucoup plus rapide)
    """
    bulk_ops = []
    for mot, livres in mot_index.items():
        bulk_ops.append({
            "update_one": {
                "filter": {"mot": mot},
                "update": {"$set": {"livres": livres}},
                "upsert": True
            }
        })

    if bulk_ops:
        index_col.bulk_write(bulk_ops)
        print(f"📤 {len(bulk_ops)} mots insérés dans MongoDB (batch).")

if __name__ == "__main__":
    main()
