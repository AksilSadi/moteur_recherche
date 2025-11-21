import time
import numpy as np
from tqdm import tqdm
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db

# Connexion MongoDB
db = get_db()
index_col = db["index"]
similarity_col = db["similarity"]

# --- Création SAFE des index ---

def safe_create_index(col, name, key, **kwargs):
    """Crée un index seulement s'il n'existe pas déjà."""
    existing = col.index_information()
    
    if name not in existing:
        print(f"📌 Création de l'index {name}...")
        col.create_index(key, name=name, **kwargs)
        print("✅ Index créé.")
    else:
        print(f"ℹ️ Index {name} déjà présent — OK.")


# Index pour la collection index
safe_create_index(index_col, "mot_1", [("mot", 1)])
safe_create_index(index_col, "mot_text", [("mot", "text")])

# Index pour similarity
safe_create_index(similarity_col, "livre1_1", [("livre1", 1)])
safe_create_index(similarity_col, "livre2_1", [("livre2", 1)])


# Creer le dossier data
os.makedirs("scripts/data", exist_ok=True)
output_file = "scripts/data/jaccard_matrix.txt"

# Étape 1 — Construire les ensembles de mots par livre
print("📖 Lecture des index...")
livre_mots = {}
for entry in tqdm(index_col.find(), desc="Chargement de l'index"):
    mot = entry["mot"]
    for livre_id in entry["livres"].keys():
        livre_mots.setdefault(livre_id, set()).add(mot)

livre_ids = sorted(livre_mots.keys())
n = len(livre_ids)
print(f"✅ {n} livres trouvés.")

# Étape 2 — Calcul de la matrice Jaccard
print("🧮 Calcul de la matrice complète Jaccard...")
S = np.zeros((n, n), dtype=np.float32)
start_time = time.time()

for i in tqdm(range(n), desc="Calcul Jaccard"):
    Wi = livre_mots[livre_ids[i]]
    for j in range(i + 1, n):
        Wj = livre_mots[livre_ids[j]]
        inter = len(Wi & Wj)
        union = len(Wi | Wj)
        if union > 0:
            jacc = inter / union
            S[i, j] = S[j, i] = jacc

elapsed = time.time() - start_time
print(f"⏱️ Calcul Jaccard terminé en {elapsed:.2f} secondes.")

# Étape 3 — Écriture dans un fichier texte
print(f"💾 Sauvegarde dans {output_file}...")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(";".join(livre_ids) + "\n")
    for i in range(n):
        row = ";".join([str(v) for v in S[i]])
        f.write(row + "\n")

print(f"✅ Fichier texte Jaccard créé ({n}x{n}).")

# Étape 4 — Sauvegarde dans MongoDB
print("📤 Sauvegarde des similarités non nulles dans MongoDB...")
similarity_col.delete_many({})
seuil = 0.4
count = 0

for i in range(n):
    for j in range(i + 1, n):
        if S[i, j] >= seuil:
            similarity_col.insert_one({
                "livre1": livre_ids[i],
                "livre2": livre_ids[j],
                "jaccard": float(S[i, j])
            })
            count += 1

print(f"✅ {count} couples sauvegardés dans similarity.")

close_db()
