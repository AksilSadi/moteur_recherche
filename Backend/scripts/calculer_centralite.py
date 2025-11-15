import time
import numpy as np
import networkx as nx
from tqdm import tqdm
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, close_db

#  Connexion MongoDB + SAFE INDEX
db = get_db()
centrality_col = db["centrality"]

def safe_create_index(col, name, key, **kwargs):
    """Crée un index seulement s'il n'existe pas déjà."""
    existing = col.index_information()
    if name not in existing:
        print(f"📌 Création de l'index {name}...")
        col.create_index(key, name=name, **kwargs)
        print("✅ Index créé.")
    else:
        print(f"ℹ️ Index {name} déjà présent — OK.")

# Crée un index sur livreId
safe_create_index(centrality_col, "livreId_1", [("livreId", 1)])


#  Dossiers et fichiers
os.makedirs("scripts/data", exist_ok=True)
input_file = "scripts/data/jaccard_matrix.txt"
output_file = "scripts/data/centrality_results.txt"


#  Etape 1: Lecture matrice Jaccard
print("📄 Lecture de la matrice Jaccard depuis le fichier...")

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

livre_ids = lines[0].strip().split(";")
n = len(livre_ids)
print(f"✅ {n} livres chargés.")

S = np.array([list(map(float, line.strip().split(";"))) for line in lines[1:]])
print(f"✅ Matrice Jaccard rechargée : {S.shape}")


#  Etape 2: Construction du graphe NetworkX
print("🌐 Construction du graphe pondéré...")
G = nx.Graph()

for lid in livre_ids:
    G.add_node(lid)

seuil = 0.01
for i in range(n):
    for j in range(i + 1, n):
        poids = S[i, j]
        if poids >= seuil:
            # distance calculée pour l’inverse du poids
            G.add_edge(
                livre_ids[i], 
                livre_ids[j],
                weight=poids,
                distance=1.0 / (poids + 1e-9)
            )

print(f"✅ Graphe créé avec {G.number_of_nodes()} nœuds et {G.number_of_edges()} arêtes.")


#  Etape 3: Calcul des centralités
start_time = time.time()
print("⚙️ Calcul des centralités...")

# Closeness centrality
t0 = time.time()
closeness = nx.closeness_centrality(G, distance="distance")
print(f"   - Closeness en {time.time() - t0:.2f}s")

# Betweenness centrality
t0 = time.time()
betweenness = nx.betweenness_centrality(G, weight="distance")
print(f"   - Betweenness en {time.time() - t0:.2f}s")

# PageRank
t0 = time.time()
pagerank = nx.pagerank(G, weight="weight")
print(f"   - PageRank en {time.time() - t0:.2f}s")

print(f"✅ Centralités calculées en {time.time() - start_time:.2f} secondes.")

#  Etape 4 — Sauvegarde MongoDB
print("📤 Sauvegarde MongoDB...")

centrality_col.delete_many({})

for lid in livre_ids:
    centrality_col.insert_one({
        "livreId": lid,
        "closeness": float(closeness.get(lid, 0)),
        "betweenness": float(betweenness.get(lid, 0)),
        "pagerank": float(pagerank.get(lid, 0))
    })

print(f"✅ {len(livre_ids)} documents insérés dans centrality.")

#  Etape 5: Sauvegarde fichier texte
print(f"💾 Sauvegarde dans {output_file}...")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("livreId;closeness;betweenness;pagerank\n")
    for lid in livre_ids:
        f.write(f"{lid};{closeness.get(lid, 0):.6f};{betweenness.get(lid, 0):.6f};{pagerank.get(lid, 0):.6f}\n")

print("✅ Fichier centrality_results.txt enregistré.")

#  Etape 6: Statistiques console
print("📊 Exemples :")
print("Top 5 Closeness:", sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:5])
print("Top 5 Betweenness:", sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5])
print("Top 5 PageRank:", sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5])

close_db()
