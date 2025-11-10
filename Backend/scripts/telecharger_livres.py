import os
import requests
from pymongo import MongoClient
import re
from datetime import datetime

# 1) Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['bibliotheque']
livres_collection = db['livres']
# 2) Création du dossier pour les livres
dossier_livres = 'livres'
if not os.path.exists(dossier_livres):
    os.makedirs(dossier_livres)
# 3) Fonctions utilitaires (compter mots, télécharger, etc.)
def compter_mots(texte):
    """Compte le nombre de mots dans un texte donné."""
    mots = re.findall(r'\b\w+\b', texte)
    return len(mots)
def telecharger_livre(url, chemin_fichier):
    """Télécharge un livre depuis une URL, le sauvegarde, et renvoie le texte."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie que la requête a réussi
        texte = response.text        # texte en string

        # Sauvegarder en UTF-8
        with open(chemin_fichier, 'w', encoding='utf-8') as fichier:
            fichier.write(texte)

        print(f"Téléchargé avec succès : {chemin_fichier}")
        return texte
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de {url} : {e}")
        return None
# 4) Boucle principale

def main():
    print("Démarrage du script de téléchargement de livres...")
    print("Nombre de livres déjà en base :", livres_collection.count_documents({}))

    page = 1
    livres_sauvegardes = 0
    livres_voulus = 1664
    min_mots = 10000

    while livres_sauvegardes < livres_voulus:
        print(f"📖 Récupération de la page {page} depuis Gutendex...")
        url_api = f"https://gutendex.com/books/?page={page}"
        reponse = requests.get(url_api)

        if reponse.status_code != 200:
            print(f"⚠️ Erreur API (code {reponse.status_code})")
            break

        data = reponse.json()
        livres = data.get("results", [])

        # Parcours de chaque livre de la page
        for livre in livres:
            # Vérifier si déjà en base
            if livres_collection.find_one({"gutendexId": livre["id"]}):
                print(f"⏭️ Livre {livre['title']} déjà présent, on saute.")
                continue

            # Chercher le lien texte
            formats = livre.get("formats", {})
            lien_texte = None
            for fmt in ["text/plain; charset=utf-8", "text/plain", "text/plain; charset=us-ascii"]:
                if fmt in formats:
                    lien_texte = formats[fmt]
                    break

            if not lien_texte:
                continue  # pas de texte brut, on ignore

            # Télécharger et compter les mots
            chemin_fichier = os.path.join(dossier_livres, f"livre_{livre['id']}.txt")
            texte = telecharger_livre(lien_texte, chemin_fichier)
            if not texte:
                continue

            nb_mots = compter_mots(texte)
            if nb_mots < min_mots:
                print(f"📉 Livre trop court ({nb_mots} mots) : {livre['title']}")
                continue

            # Extraire infos principales
            auteur = livre["authors"][0]["name"] if livre.get("authors") else "Inconnu"

            # Insérer dans MongoDB
            doc = {
                "gutendexId": livre["id"],
                "titre": livre["title"],
                "auteur": auteur,
                "chemin": chemin_fichier,
                "nombreMots": nb_mots,
                "downloadCount": livre.get("download_count", 0),
                "dateAjout": datetime.now()
            }
            livres_collection.insert_one(doc)
            livres_sauvegardes += 1

            print(f"✅ Livre enregistré : {livre['title']} ({nb_mots} mots) — Total : {livres_sauvegardes}")

            if livres_sauvegardes >= livres_voulus:
                break

        if not data.get("next"):
            print("🚫 Plus de pages disponibles dans l'API.")
            break

        page += 1

    print(f"✅ Terminé ! {livres_sauvegardes} livres enregistrés dans MongoDB.")


if __name__ == "__main__":
    main()