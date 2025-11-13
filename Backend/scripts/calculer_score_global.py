
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db
# Connexion MongoDB
db=get_db()
centr_col = db["centrality"]
livres_col = db["livres"]

# Créer le dossier data s’il n’existe pas
os.makedirs("scripts/data", exist_ok=True)
output_file = "scripts/data/score_global_results.txt"

# Etape 1 — Récupération des données

print("📥 Lecture des centralités et popularités depuis MongoDB...")

docs = list(centr_col.find())
print(f"✅ {len(docs)} documents trouvés dans 'centrality'.")

# Récupérer la popularité (downloads) des livres
popularite = {str(l["gutendexId"]): l.get("downloadCount", 0) for l in livres_col.find()}

# Etape 2 — Normalisation min-max
def normaliser(valeurs_dict):
    if not valeurs_dict:
        return {}
    vals = list(valeurs_dict.values())
    vmin, vmax = min(vals), max(vals)
    eps = 1e-9
    return {k: (v - vmin) / (vmax - vmin + eps) for k, v in valeurs_dict.items()}

def normaliser_depuis_centrality(champ):
    valeurs = {d["livreId"]: d.get(champ, 0.0) for d in docs}
    return normaliser(valeurs)

pagerank_norm = normaliser_depuis_centrality("pagerank")
closeness_norm = normaliser_depuis_centrality("closeness")
betweenness_norm = normaliser_depuis_centrality("betweenness")
popularite_norm = normaliser(popularite)

print("✅ Normalisation effectuée pour toutes les mesures.")

# Etape 3 — Poids et calcul du score global
poids = {
    "pagerank": 0.4,
    "closeness": 0.3,
    "betweenness": 0.1,
    "popularite": 0.2
}

print("⚙️ Calcul du score global pondéré...")

results = []
start_time = time.time()

for d in docs:
    lid = d["livreId"]
    score = (
        poids["pagerank"] * pagerank_norm.get(lid, 0) +
        poids["closeness"] * closeness_norm.get(lid, 0) +
        poids["betweenness"] * betweenness_norm.get(lid, 0) +
        poids["popularite"] * popularite_norm.get(lid, 0)
    )

    # Mettre à jour le document Mongo
    centr_col.update_one(
        {"livreId": lid},
        {"$set": {"scoreGlobal": float(score)}}
    )

    results.append((lid, score))

elapsed = time.time() - start_time
print(f"✅ Score global calculé pour {len(results)} livres en {elapsed:.2f} secondes.")

# Etape 4 — Sauvegarde dans un fichier texte

print(f"💾 Sauvegarde des scores dans {output_file}...")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("livreId;scoreGlobal\n")
    for lid, s in sorted(results, key=lambda x: x[1], reverse=True):
        f.write(f"{lid};{s:.6f}\n")

print(f"✅ Fichier enregistré : {output_file}")

# Etape 5 — Exemples des meilleurs livres

top10 = sorted(results, key=lambda x: x[1], reverse=True)[:10]
print("\n🏆 Top 10 livres (score global) :")
for lid, score in top10:
    livre = livres_col.find_one({"gutendexId": int(lid)})
    titre = livre.get("title", "Sans titre") if livre else "Inconnu"
    print(f" - {titre[:60]}...  →  score = {score:.4f}")

close_db()