import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db

# --- Fichier Jaccard déjà généré ---
input_file = "scripts/data/jaccard_matrix.txt"

os.makedirs("results", exist_ok=True)

# --- Étape 1 : Lecture de la matrice ---
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

livre_ids = lines[0].strip().split(";")
n = len(livre_ids)

S = np.array([list(map(float, line.strip().split(";"))) for line in lines[1:]])

print(f"📚 Matrice chargée ({n} livres).")

# --- Étape 2 : Construction du graphe ---
G = nx.Graph()

seuil = 0.4
for lid in livre_ids:
    G.add_node(lid)

for i in range(n):
    for j in range(i + 1, n):
        w = S[i, j]
        if w >= seuil:
            G.add_edge(
                livre_ids[i],
                livre_ids[j],
                weight=w,
                distance=1 / (w + 1e-9)
            )

print(f"🌐 Graphe : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes.")


# ============================================================
# 1) EXPÉRIMENTATION TEMPS CENTRALITÉ
# ============================================================

def measure_time(func, *args, **kwargs):
    """Mesure le temps d'exécution d'une fonction."""
    t0 = time.time()
    val = func(*args, **kwargs)
    return val, time.time() - t0


print("\n⏳ Mesure des temps de centralité…")

# CORRIGÉ : arguments nommés
closeness, t_clo = measure_time(nx.closeness_centrality, G, distance="distance")
betweenness, t_bet = measure_time(nx.betweenness_centrality, G, weight="distance")
pagerank, t_pr = measure_time(nx.pagerank, G, weight="weight")

print(f"➡️ Closeness : {t_clo:.2f}s")
print(f"➡️ Betweenness : {t_bet:.2f}s")
print(f"➡️ PageRank : {t_pr:.2f}s")


# --- Bar chart temps ---
plt.figure(figsize=(8, 5))
plt.bar(["Closeness", "Betweenness", "PageRank"],
        [t_clo, t_bet, t_pr],
        color=["blue", "green", "red"])
plt.ylabel("Temps (sec)")
plt.title("Temps de calcul des centralités")
plt.grid(axis="y")
plt.savefig("results/centrality_times.png")
plt.show()

print("📊 Graphique centrality_times.png généré.")


# 2) EXPÉRIMENTATION : CONVERGENCE DE PAGERANK

def pagerank_iterations(G, max_iter=80):
    """PageRank manuelle (pas NetworkX) pour mesurer la convergence."""
    nodes = list(G.nodes())
    n = len(nodes)

    pr_old = {u: 1/n for u in nodes}
    diffs = []

    # Construction graphe pondéré normalisé
    W = {}
    for u, v, data in G.edges(data=True):
        w = data.get("weight", 1.0)
        W.setdefault(u, {})[v] = w
        W.setdefault(v, {})[u] = w

    out_sum = {u: sum(W[u].values()) for u in W}

    alpha = 0.85

    for _ in range(max_iter):
        pr_new = {}
        for u in nodes:
            s = sum(pr_old[v] * (W[v][u] / out_sum[v]) for v in W.get(u, {}))
            pr_new[u] = (1 - alpha)/n + alpha * s

        diffs.append(sum(abs(pr_new[u] - pr_old[u]) for u in nodes))
        pr_old = pr_new

    return diffs



print("\n📈 Calcul convergence PageRank…")
diffs = pagerank_iterations(G, max_iter=80)

# --- Courbe convergence ---
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(diffs) + 1), diffs, marker="o")
plt.xlabel("Itération k")
plt.ylabel("||PR(k)-PR(k-1)||")
plt.title("Convergence de PageRank")
plt.grid(True)
plt.savefig("results/pagerank_convergence.png")
plt.show()

print("📈 Courbe générée : results/pagerank_convergence.png")

# 3) ILLUSTRATION : CENTRALITÉS POUR QUELQUES LIVRES

print("\n📘 Extraction des centralités pour quelques livres...")

# Choisir manuellement 5 livres intéressants (tu peux changer)
EXAMPLE_IDS = ["84", "174", "2701", "11", "1342"]  
# Frankenstein, Dracula, Moby Dick, Alice, Pride & Prejudice

# Récupération des titres depuis Mongo
db = get_db()
livres_col = db["livres"]

titles = []
records = []

for lid in EXAMPLE_IDS:
    # Cherche dans Mongo
    book = livres_col.find_one({"gutendexId": int(lid)}, {"titre": 1})
    if not book:
        continue

    titles.append(book["titre"])

    records.append({
        "closeness": closeness.get(lid, 0),
        "betweenness": betweenness.get(lid, 0),
        "pagerank": pagerank.get(lid, 0)
    })

print("\n=== VALEURS BRUTES ===")
for title, r in zip(titles, records):
    print(f"{title}: C={r['closeness']:.5f}  B={r['betweenness']:.6f}  PR={r['pagerank']:.6f}")

# --- Graphique centralités pour exemple ---
plt.figure(figsize=(12,6))
x = range(len(records))

plt.bar([i - 0.2 for i in x], [r["closeness"] for r in records],
        width=0.2, label="Closeness", color="steelblue")

plt.bar(x, [r["betweenness"] for r in records],
        width=0.2, label="Betweenness", color="orange")

plt.bar([i + 0.2 for i in x], [r["pagerank"] for r in records],
        width=0.2, label="PageRank", color="green")

plt.xticks(x, titles, rotation=40, ha="right")
plt.ylabel("Valeurs normalisées")
plt.title("Centralités pour quelques livres exemples")
plt.legend()
plt.grid(axis="y")

plt.tight_layout()
plt.savefig("results/centrality_examples.png")
plt.show()

print("📊 Graphique 'centrality_examples.png' généré.")
