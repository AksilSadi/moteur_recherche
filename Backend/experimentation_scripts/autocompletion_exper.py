import time
import matplotlib.pyplot as plt
import os
import sys

# Importation projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.trie_builder import TRIE_INSTANCE, build_trie_filtered_by_index

os.makedirs("results", exist_ok=True)

# PARTIE 1: PERFORMANCE (TRIE)

PREFIXES_PERF = ["l", "lo", "lov", "love", "k", "ki", "kin", "king"]

def measure(prefix):
    t0 = time.time()
    res = TRIE_INSTANCE.autocomplete(prefix.lower())
    dt = (time.time() - t0) * 1000  # ms
    return dt, len(res)

times = []
counts = []

print("\n=== PERFORMANCE AUTOCOMPLETION (TRIE) ===\n")

for p in PREFIXES_PERF:
    dt, c = measure(p)
    print(f"{p:<10} → {dt:.2f} ms | {c} suggestions")
    times.append(dt)
    counts.append(c)

# --- Bar Chart (temps)
plt.figure(figsize=(10,5))
plt.bar(PREFIXES_PERF, times, color="steelblue")
plt.title("Temps de réponse de l’autocomplétion (TRIE)")
plt.xlabel("Préfixe")
plt.ylabel("Temps (ms)")
plt.grid(axis="y")
plt.savefig("results/autocomplete_trie_time_barchart.png")
plt.show()

# --- Bar Chart (nb de suggestions)
plt.figure(figsize=(10,5))
plt.bar(PREFIXES_PERF, counts, color="darkorange")
plt.title("Nombre de suggestions TRIE")
plt.xlabel("Préfixe")
plt.ylabel("Nombre de suggestions")
plt.grid(axis="y")
plt.savefig("results/autocomplete_trie_suggestions_barchart.png")
plt.show()



# PARTIE 2 : TEMPS DE CONSTRUCTION DU TRIE

TEST_SIZES = [50, 100, 200, 400, 800, 1664]

sizes2, times2 = [], []

print("\n=== TEMPS DE CONSTRUCTION DU TRIE ===\n")

for n in TEST_SIZES:
    print(f"Construction TRIE basée sur {n} livres...")
    t0 = time.time()
    _ = build_trie_filtered_by_index(nb_livres=n)
    t = time.time() - t0

    print(f"→ {t:.2f} sec\n")
    sizes2.append(n)
    times2.append(t)

# Courbe de construction
plt.figure(figsize=(10,5))
plt.plot(sizes2, times2, marker="o", color="purple")
plt.title("Temps de construction du TRIE")
plt.xlabel("Nombre de livres utilisés")
plt.ylabel("Temps (sec)")
plt.grid(True)
plt.savefig("results/autocomplete_trie_build_time.png")
plt.show()


print("\n📊 Graphiques générés :")
print(" - autocomplete_trie_time_barchart.png")
print(" - autocomplete_trie_suggestions_barchart.png")
print(" - autocomplete_trie_build_time.png")
