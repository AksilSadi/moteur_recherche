import time
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db
from services.search import search
import os

# Créer dossier results/ si pas encore créé
os.makedirs("results", exist_ok=True)

db = get_db()

TEST_QUERIES = [
    ("sargon", "keyword"),
    ("king", "keyword"),
    ("^the.*", "regex"),
    ("princess", "regex"),
]

def measure(q, mode):
    t0 = time.time()
    _ = search(q, mode)
    return (time.time() - t0) * 1000  # ms


print("\n=== Benchmark Recherche ===\n")
labels = []   # juste les mots
times = []    # temps pour chaque requête

for q, mode in TEST_QUERIES:
    t = measure(q, mode)
    print(f"{q:<12} ({mode}) → {t:.2f} ms")

    labels.append(q)   
    times.append(t)

# ======== GRAPHIQUE =========

plt.figure(figsize=(12,6))
plt.bar(labels, times, color=['#1f77b4', '#1f77b4', '#ff7f0e', '#ff7f0e'])
plt.ylabel("Temps (ms)")
plt.title("Performance de recherche")
plt.grid(axis='y')

# Afficher les valeurs au-dessus des barres
for i, v in enumerate(times):
    plt.text(i, v + 2, f"{v:.1f}", ha="center", fontsize=9)

out_path = "results/performance_recherche.png"
plt.savefig(out_path, dpi=150)
plt.show()

print(f"\n📊 Graphique généré : {out_path}")
