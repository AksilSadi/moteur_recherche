from typing import List

def creer_CO(mot: str) -> List[int]:
    """Étape 1 : tableau next classique (CO) avec sentinelle -1."""
    m = len(mot)
    CO = [-1] + [0] * m
    i, j = 0, -1
    while i < m:
        if j == -1 or mot[i] == mot[j]:
            i += 1
            j += 1
            CO[i] = j
        else:
            j = CO[j]
    return CO


def creer_tableau_CO1(CO: List[int], mot: str) -> List[int]:
    """Étape 2 : remplace certains 0 par -1 si mot[i] == mot[0]."""
    t = CO.copy()
    for i in range(1, len(mot)):
        if t[i] == 0 and mot[i] == mot[0]:
            t[i] = -1
    return t


def creer_tableau_CO2(CO1: List[int], mot: str) -> List[int]:
    """Étape 3 : optimisation finale."""
    t = CO1.copy()
    m = len(mot)
    for i in range(1, m + 1):
        if t[i] != -1 and i < m:
            j = t[i]
            if 0 <= j < len(t) and t[j] != -1:
                if mot[i] == mot[j]:
                    t[i] = t[j]
    return t


def kmp_search(text: str, mot: str) -> List[int]:
    """Recherche toutes les occurrences de `mot` dans `text`."""
    matches = []
    if not text or not mot:
        return matches

    n, m = len(text), len(mot)
    if m == 0:
        return list(range(n + 1))

    CO = creer_CO(mot)
    CO1 = creer_tableau_CO1(CO, mot)
    CO2 = creer_tableau_CO2(CO1, mot)

    i = j = 0
    while i < n:
        if j == -1 or text[i] == mot[j]:
            i += 1
            j += 1
            if j == m:
                matches.append(i - m)
                j = CO2[j]
        else:
            j = CO2[j]
    return matches

