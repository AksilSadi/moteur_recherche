import os
import re
import requests
from datetime import datetime
import sys

# --- Import du module database ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db

# --- Connexion MongoDB ---
db = get_db()
livres_collection = db["livres"]

# --- Dossier pour stocker les fichiers texte ---
DOSSIER_LIVRES = "livres"
os.makedirs(DOSSIER_LIVRES, exist_ok=True)


# --- Fonction : compter les mots d’un texte ---
def compter_mots(texte: str) -> int:
    """Compte le nombre de mots dans un texte donné."""
    return len(re.findall(r"\b\w+\b", texte))


# --- Fonction : télécharger un livre (texte brut) ---
def telecharger_livre(url: str, chemin_fichier: str):
    """Télécharge un livre depuis une URL et sauvegarde le texte brut localement."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        texte = r.text
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write(texte)
        print(f"📘 Livre téléchargé : {chemin_fichier}")
        return texte
    except Exception as e:
        print(f"⚠️ Erreur téléchargement {url}: {e}")
        return None


# --- Fonction : récupérer l’URL de couverture (sans téléchargement) ---
def trouver_cover_url(livre):
    """Construit les URLs possibles pour la couverture Gutenberg et teste la première valide."""
    formats = livre.get("formats", {})
    if "image/jpeg" in formats:
        return formats["image/jpeg"]  # Lien direct fourni par l’API Gutendex

    # Sinon, essaie les formats standards Gutenberg
    possible_urls = [
        f"https://www.gutenberg.org/files/{livre['id']}/{livre['id']}-h/images/cover.jpg",
        f"https://www.gutenberg.org/cache/epub/{livre['id']}/pg{livre['id']}.cover.medium.jpg"
    ]

    for url in possible_urls:
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                return url
        except:
            continue
    return None


# --- Script principal ---
def main():
    print("🚀 Démarrage du téléchargement des livres + URL des images...")
    print("📚 Livres déjà en base :", livres_collection.count_documents({}))

    page = 1
    livres_sauvegardes = 0
    livres_voulus = 1664
    min_mots = 10000

    while livres_sauvegardes < livres_voulus:
        print(f"\n📖 Page {page} — Récupération depuis Gutendex...")
        response = requests.get(f"https://gutendex.com/books/?page={page}")
        if response.status_code != 200:
            print(f"⚠️ Erreur API (code {response.status_code})")
            break

        data = response.json()
        livres = data.get("results", [])

        for livre in livres:
            # Vérifie s'il est déjà en base
            if livres_collection.find_one({"gutendexId": livre["id"]}):
                continue

            # Trouve un lien texte brut
            formats = livre.get("formats", {})
            lien_texte = next(
                (formats.get(fmt) for fmt in [
                    "text/plain; charset=utf-8",
                    "text/plain",
                    "text/plain; charset=us-ascii"
                ] if fmt in formats),
                None
            )

            if not lien_texte:
                continue

            # Téléchargement du texte
            chemin_fichier = os.path.join(DOSSIER_LIVRES, f"livre_{livre['id']}.txt")
            texte = telecharger_livre(lien_texte, chemin_fichier)
            if not texte:
                continue

            nb_mots = compter_mots(texte)
            if nb_mots < min_mots:
                print(f"📉 Livre trop court ({nb_mots} mots) : {livre['title']}")
                continue

            # Récupération de la couverture (URL uniquement)
            cover_url = trouver_cover_url(livre)

            # Informations principales
            auteur = livre["authors"][0]["name"] if livre.get("authors") else "Inconnu"

            # Insertion dans MongoDB
            doc = {
                "gutendexId": livre["id"],
                "titre": livre["title"],
                "auteur": auteur,
                "chemin": chemin_fichier,
                "coverUrl": cover_url, 
                "nombreMots": nb_mots,
                "downloadCount": livre.get("download_count", 0),
                "dateAjout": datetime.now()
            }
            livres_collection.insert_one(doc)
            livres_sauvegardes += 1

            print(f"✅ Livre enregistré : {livre['title']} — Total : {livres_sauvegardes}")

            if livres_sauvegardes >= livres_voulus:
                break

        if not data.get("next"):
            print("🚫 Plus de pages disponibles.")
            break

        page += 1

    print(f"\n🎯 Terminé : {livres_sauvegardes} livres enregistrés avec coverUrl.")
    close_db()


if __name__ == "__main__":
    main()
