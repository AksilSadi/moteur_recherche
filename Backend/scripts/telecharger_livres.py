import os
import re
import time
import requests
from datetime import datetime
import sys

# --- Import du module database ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db

# --- Connexion MongoDB ---
db = get_db()
livres_collection = db["livres"]

# --- Création de l’index uniquement s'il n'existe pas déjà ---
indexes = livres_collection.index_information()
if "gutendexId_1" not in indexes:
    print("Création de l'index unique sur gutendexId...")
    livres_collection.create_index(
        [("gutendexId", 1)],
        unique=True,
        name="gutendexId_1"
    )
    print("✅ Index créé.")
else:
    print("Index 'gutendexId_1' déjà existant — aucune action requise.")

# --- Dossier pour stocker les fichiers texte ---
DOSSIER_LIVRES = "livres"
os.makedirs(DOSSIER_LIVRES, exist_ok=True)

# --- Paramètres globaux ---
MIN_MOTS = 10000
NB_LIVRES_VOULUS = 1664
GUTENDEX_BASE_URL = "https://gutendex.com/books/"
HEADERS = {
    "User-Agent": "M2-STL-DAAR-book-crawler/1.0 (contact: projet-etudiant)"
}


# --- Fonction : compter les mots d’un texte ---
def compter_mots(texte: str) -> int:
    return len(re.findall(r"\b\w+\b", texte))


# --- Fonction générique : GET JSON avec retries ---
def get_json_with_retry(url: str, session: requests.Session, max_retries: int = 5, timeout: int = 20):
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur réseau JSON sur {url}: {e}, tentative {attempt}/{max_retries}")
            if attempt == max_retries:
                print(f"❌ Abandon pour {url}")
                return None
            time.sleep(2 * attempt)  # backoff progressif


# --- Fonction : télécharger un livre (texte brut) avec retries ---
def telecharger_livre(url: str, chemin_fichier: str, session: requests.Session, max_retries: int = 3, timeout: int = 20):
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            texte = r.text
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write(texte)
            print(f"📘 Livre téléchargé : {chemin_fichier}")
            return texte
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur téléchargement {url}: {e}, tentative {attempt}/{max_retries}")
            if attempt == max_retries:
                print(f"❌ Abandon du téléchargement du texte pour {url}")
                return None
            time.sleep(2 * attempt)  # backoff


# --- Fonction : récupérer l’URL de couverture (sans téléchargement) ---
def trouver_cover_url(livre, session: requests.Session):
    formats = livre.get("formats", {})

    # Si Gutendex fournit déjà l'image
    if "image/jpeg" in formats:
        return formats["image/jpeg"]

    # Sinon tester les URLs standard de Gutenberg
    possible_urls = [
        f"https://www.gutenberg.org/files/{livre['id']}/{livre['id']}-h/images/cover.jpg",
        f"https://www.gutenberg.org/cache/epub/{livre['id']}/pg{livre['id']}.cover.medium.jpg"
    ]

    for url in possible_urls:
        try:
            resp = session.head(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                return url
        except requests.exceptions.RequestException:
            continue
    return None


# --- Script principal ---
def main():
    print("🚀 Démarrage du téléchargement des livres avec métadonnées enrichies...")
    deja_en_base = livres_collection.count_documents({})
    print("📚 Livres déjà en base :", deja_en_base)

    session = requests.Session()

    page = 1
    livres_sauvegardes = deja_en_base  # si la base est déjà partiellement remplie
    livres_voulus = NB_LIVRES_VOULUS
    min_mots = MIN_MOTS

    # On boucle tant qu'on n'a pas atteint le nombre souhaité de livres
    # et qu'il reste des pages à explorer
    while livres_sauvegardes < livres_voulus:
        print(f"\n📖 Page {page} — Récupération depuis Gutendex...")
        url_page = f"{GUTENDEX_BASE_URL}?page={page}"

        data = get_json_with_retry(url_page, session=session, max_retries=5, timeout=20)
        if data is None:
            # On n'arrête pas tout le script, on tente la page suivante
            print(f"❌ Impossible de récupérer la page {page}, on passe à la suivante.")
            page += 1
            # Pause pour ne pas spammer l'API
            time.sleep(1)
            continue

        livres = data.get("results", [])
        if not livres:
            print("🚫 Aucun résultat sur cette page, arrêt.")
            break

        for livre in livres:
            gutendex_id = livre["id"]

            # Vérifie s'il est déjà en base
            if livres_collection.find_one({"gutendexId": gutendex_id}):
                continue

            # Récupérer un lien texte brut
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

            chemin_fichier = os.path.join(DOSSIER_LIVRES, f"livre_{gutendex_id}.txt")
            texte = telecharger_livre(lien_texte, chemin_fichier, session=session)
            if not texte:
                continue

            nb_mots = compter_mots(texte)
            if nb_mots < min_mots:
                print(f"📉 Livre trop court ({nb_mots} mots) : {livre['title']}")
                # On peut supprimer le fichier texte pour économiser de la place
                try:
                    os.remove(chemin_fichier)
                except OSError:
                    pass
                continue

            cover_url = trouver_cover_url(livre, session=session)
            auteur = livre["authors"][0]["name"] if livre.get("authors") else "Inconnu"
            birth_year = livre["authors"][0].get("birth_year") if livre.get("authors") else None
            death_year = livre["authors"][0].get("death_year") if livre.get("authors") else None
            subjects = livre.get("subjects", [])
            languages = livre.get("languages", [])
            rights = livre.get("rights", None)
            bookshelves = livre.get("bookshelves", [])
            media_type = livre.get("media_type", None)
            gutenberg_url = f"https://www.gutenberg.org/ebooks/{gutendex_id}"

            # --- Insertion MongoDB ---
            doc = {
                "gutendexId": gutendex_id,
                "titre": livre["title"],
                "auteur": auteur,
                "chemin": chemin_fichier,
                "coverUrl": cover_url,
                "nombreMots": nb_mots,
                "downloadCount": livre.get("download_count", 0),
                "dateAjout": datetime.now(),
                "birthYear": birth_year,
                "deathYear": death_year,
                "subjects": subjects,
                "languages": languages,
                "rights": rights,
                "bookshelves": bookshelves,
                "mediaType": media_type,
                "gutenbergUrl": gutenberg_url
            }

            try:
                livres_collection.insert_one(doc)
                livres_sauvegardes += 1
                print(f"✅ Livre enregistré : {livre['title']} — Total : {livres_sauvegardes}")
            except Exception as e:
                print(f"⚠️ Erreur insertion Mongo pour {gutendex_id} : {e}")
                # on peut aussi supprimer le fichier texte en cas d'échec insertion
                try:
                    os.remove(chemin_fichier)
                except OSError:
                    pass

            if livres_sauvegardes >= livres_voulus:
                break

        # Si l'API indique qu'il n'y a plus de page suivante, on sort
        if not data.get("next"):
            print("🚫 Plus de pages disponibles.")
            break

        page += 1
        # Petite pause pour ne pas surcharger l'API
        time.sleep(1)

    print(f"\n🎯 Terminé : {livres_sauvegardes} livres enregistrés avec métadonnées enrichies.")
    close_db()


if __name__ == "__main__":
    main()
