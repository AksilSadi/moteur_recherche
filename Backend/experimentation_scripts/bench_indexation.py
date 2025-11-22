import random
import time
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db
from for_experimentation.indexation_core import indexer_un_livre_local, fusionner_local

# Création du dossier results s'il n'existe pas
os.makedirs("results", exist_ok=True)

TEST_SIZES = [10, 50, 100, 200, 400, 800, 1664]

db = get_db()
livres_col = db["livres"]


def bench(n):
    """Retourne : temps_indexation, nombre_de_mots_indexés"""
    livres = list(livres_col.find({}, {"_id": 0}))
    random.shuffle(livres)
    livres = livres[:n]

    start = time.time()

    # indexation
    resultats = []
    for livre in livres:
        r = indexer_un_livre_local(livre)
        if r:
            resultats.append(r)

    mot_index = fusionner_local(resultats)

    t = time.time() - start
    return t, len(mot_index)


# Lancement benchmark
sizes = []
times = []
word_counts = []

print("\n=== BENCHMARK INDEXATION ===\n")

for n in TEST_SIZES:
    print(f"⏳ Test sur {n} livres…")
    t, count = bench(n)
    print(f"➡️ Temps : {t:.2f} s – Mots indexés : {count}\n")

    sizes.append(n)
    times.append(t)
    word_counts.append(count)


# === GRAPHIQUE 1 — Courbe du temps d’indexation ===
plt.figure(figsize=(10, 6))
plt.plot(sizes, times, marker="o", color="blue", label="Temps d'indexation (sec)")
plt.xlabel("Nombre de livres")
plt.ylabel("Temps (sec)")
plt.title("Benchmark d'indexation")
plt.grid(True)
plt.legend()

plt.savefig("results/benchmark_indexation_time.png")
print("📈 Courbe générée : results/benchmark_indexation_time.png")
plt.show()

# === GRAPHIQUE 2 — Bar Chart du nombre de mots indexés ===
plt.figure(figsize=(10, 6))
plt.bar([str(s) for s in sizes], word_counts, color="orange")
plt.xlabel("Nombre de livres")
plt.ylabel("Mots indexés")
plt.title("Nombre de mots indexés selon la taille du corpus")
plt.grid(axis="y")

plt.savefig("results/benchmark_indexation_wordcount.png")
print("📊 Bar Chart généré : results/benchmark_indexation_wordcount.png")

plt.show()
