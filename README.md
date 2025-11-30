# 📘 Projet : Moteur de Recherche Documentaire (Python / FastAPI / MongoDB / React)

## 🚀 Présentation du projet

Ce projet implémente un moteur de recherche complet basé sur un pipeline de traitement documentaire comprenant :

- Téléchargement automatisé de livres via **l’API Gutendex**
- Prétraitement NLP : nettoyage, suppression des stopwords, lemmatisation, fréquence (TF)
- Indexation des mots dans **MongoDB**
- Calcul de similarité entre documents (Jaccard)
- Construction d’un graphe documentaire
- Calcul des centralités : **degré**, **closeness**, **betweenness**
- Génération d’une structure **Trie** pour l’autocomplétion
- Serveur API avec **FastAPI**
- Interface web développée en **React + Vite**

L’ensemble forme une chaîne cohérente permettant une recherche performante, rapide et enrichie.

---

## 🧰 1. Installation du Backend (FastAPI)

### ✔️ Prérequis
- Python **3.10+**
- pip
- MongoDB lancé sur `mongodb://localhost:27017`

---

### 🔧 Étape 1 : Créer et activer l’environnement virtuel

Dans le dossier `backend/` :

```bash
python -m venv venv
```

#### Activation :
windows:

```bash
.\venv\Scripts\activate
```

Linux / MacOS:

```bash
source venv/bin/activate
```

### 🔧 Étape 2 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### 🗄️ Étape 3 : Vérifier que MongoDB est lancé

Sous Windows :

```bash
net start MongoDB
```

## 📚 2. Pipeline de Prétraitement (Scripts)

Tous les scripts se trouvent dans :

```bash
backend/scripts/
```

et on doit suivre cette ordre

### ▶ Script 1 - Téléchargement des livres

Télécharge les livres, leurs métadonnées, le texte brut et les couvertures.

```bash
python telecharger_livres.py
```

### ▶ Script 2 - Indexation NLP

Nettoyage du texte, filtrage des stopwords, lemmatisation, calcul des fréquences TF et stockage de l’index dans MongoDB.

```bash
python indexer_livres.py
```

### ▶ Script 3 - Calcul de similarité Jaccard

Construit la matrice de similarité entre tous les livres et enregistre les valeurs dans MongoDB.

```bash
python calcul_jaccard.py
```

### ▶ Script 4 - Calcul des centralités

Génère :

-la centralité de degré
-la centralité de closeness
-la centralité de betweenness

```bash
python calcul_centralite.py
```

### ▶ Script 5 - Calcul du score global

```bash
python calculer_score_global.py
```

## 🔌 3. Lancer l’API Backend

Dans backend/, une fois le venv activé :

```bash
uvicorn main:app --reload --port 8000
```

## 🌐 4. Installation du Frontend (React + Vite)

Dans le dossier frontend/ :

### Installer les dépendances

```bash
npm install
```

### Lancer le serveur de développement

```bash
npx vite --host
```

## 🧪 5. Expérimentations et benchmarks

Les scripts d’expérimentation sont dans :

```bash
backend/experiments/
```

Exemples :

### ▶ Jaccard benchmark

```bash
python bench_jaccard.py
```

### ▶ Indexation benchmark

```bash
python bench_indexation.py
```

## 🧱 6. Structure du projet

```bash
moteur_recherche/
│
├── backend/
│   ├── main.py                # API FastAPI
│   ├── database/              # Connexion MongoDB
│   ├── scripts/               # Téléchargement, indexation, Jaccard, centralités, Trie
│   ├── experiments/           # Tests et benchmarks
│   └── venv/                  # Environnement Python
│
└── frontend/
    ├── src/                   # Code React
    ├── public/
    └── package.json

```