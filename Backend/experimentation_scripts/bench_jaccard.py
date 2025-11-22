import time
import numpy as np
import random
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db

# Dossier résultats
os.makedirs("results", exist_ok=True)

db = get_db()
index_col = db["index"]

# tailles de test
TEST_SIZES = [50, 100, 200, 400, 800, 1200, 1600]

def charger_ensembles_mots(nb):
    """Charge nb livres depuis l'index MongoDB."""
    livre_mots = {}

    for entry in index_col.find():
        mot = entry["mot"]
        for livre_id in entry["livres"].keys():
            if livre_id not in livre_mots:
                if len(livre_mots) == nb:
                    return livre_mots
                livre_mots[livre_id] = set()
            livre_mots[livre_id].add(mot)

    return livre_mots


def bench_jaccard(nb):
    """Retourne le temps en millisecondes."""
    livre_mots = charger_ensembles_mots(nb)
    livres = list(livre_mots.keys())
    n = len(livres)

    S = np.zeros((n, n), dtype=np.float32)

    start = time.perf_counter()     # Plus précis que time.time()
    for i in range(n):
        Wi = livre_mots[livres[i]]
        for j in range(i + 1, n):
            Wj = livre_mots[livres[j]]
            inter = len(Wi & Wj)
            union = len(Wi | Wj)
            S[i, j] = S[j, i] = (inter / union) if union > 0 else 0
    end = time.perf_counter()

    return (end - start) * 1000     # conversion → millisecondes


# ---- Lancement benchmark ----
sizes = []
times = []

print("\n=== BENCHMARK MATRICE JACCARD ===\n")

for n in TEST_SIZES:
    print(f"⏳ Calcul Jaccard sur {n} livres…")
    t = bench_jaccard(n)
    print(f"➡️ Temps : {t:.2f} ms\n")
    sizes.append(n)
    times.append(t)

# ---- Courbe ----
plt.figure(figsize=(10, 6))
plt.plot(sizes, times, marker="o", color="red")
plt.xlabel("Nombre de livres")
plt.ylabel("Temps (ms)")
plt.title("Benchmark du calcul de la matrice Jaccard")
plt.grid(True)
plt.savefig("results/benchmark_jaccard.png")

print("📈 Courbe générée : results/benchmark_jaccard.png")
