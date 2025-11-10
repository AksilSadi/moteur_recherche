import time
import numpy as np
import networkx as nx
from pymongo import MongoClient
from tqdm import tqdm
import os

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["bibliotheque"]
centrality_col = db["centrality"]

# Créer le dossier data s’il n’existe pas
os.makedirs("scripts/data", exist_ok=True)
input_file = "scripts/data/jaccard_matrix.txt"
output_file = "scripts/data/centrality_results.txt"

# Etape 1 — Lecture de la matrice Jaccard
print("📄 Lecture de la matrice Jaccard depuis le fichier...")

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

livre_ids = lines[0].strip().split(";")
n = len(livre_ids)
print(f"✅ {n} livres chargés depuis la première ligne.")

S = np.array([list(map(float, line.strip().split(";"))) for line in lines[1:]])
print(f"✅ Matrice Jaccard rechargée : {S.shape}")

# Etape 2 — Construction du graphe NetworkX
print("🌐 Construction du graphe pondéré...")
G = nx.Graph()

# Ajout des nœuds
for lid in livre_ids:
    G.add_node(lid)

# Ajout des arêtes pondérées (filtrées sur un seuil)
seuil = 0.01
for i in range(n):
    for j in range(i + 1, n):
        poids = S[i, j]
        if poids >= seuil:
            # plus le jaccard est grand → plus la distance est courte
            G.add_edge(livre_ids[i], livre_ids[j], weight=poids, distance=1.0 / (poids + 1e-9))

print(f"✅ Graphe créé avec {G.number_of_nodes()} nœuds et {G.number_of_edges()} arêtes.")

# Etape 3 — Calcul des centralités
start_time = time.time()
print("⚙️ Calcul des centralités... (cela peut être long)")

# Closeness centrality (distance = inverse du poids)
closeness = nx.closeness_centrality(G, distance="distance")

# Betweenness centrality
betweenness = nx.betweenness_centrality(G, weight="distance")

# PageRank (basé sur poids Jaccard)
pagerank = nx.pagerank(G, weight="weight")

elapsed = time.time() - start_time
print(f"✅ Centralités calculées en {elapsed:.2f} secondes.")

# Etape 4 — Sauvegarde dans MongoDB
print("📤 Enregistrement dans la collection centrality...")
centrality_col.delete_many({})

for lid in livre_ids:
    centrality_col.insert_one({
        "livreId": lid,
        "closeness": float(closeness.get(lid, 0)),
        "betweenness": float(betweenness.get(lid, 0)),
        "pagerank": float(pagerank.get(lid, 0))
    })

print(f"✅ {len(livre_ids)} documents insérés dans la collection centrality.")

# Etape 5 — Sauvegarde texte (pour expérimentation)
print(f"💾 Sauvegarde des résultats dans {output_file}...")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("livreId;closeness;betweenness;pagerank\n")
    for lid in livre_ids:
        f.write(f"{lid};{closeness.get(lid, 0):.6f};{betweenness.get(lid, 0):.6f};{pagerank.get(lid, 0):.6f}\n")

print("✅ Fichier centrality_results.txt enregistré.")

# Etape 6 — Statistiques et fermeture
print(f"📊 Exemples :")
top_close = sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:5]
top_between = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]

print("Top 5 Closeness:", top_close)
print("Top 5 Betweenness:", top_between)
print("Top 5 PageRank:", top_pagerank)

client.close()
print("🔒 Connexion MongoDB fermée.")
