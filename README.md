# Systèmes de Recherche d'Information (SRI)

Projets académiques sur les systèmes de recherche d'information, implémentant différents modèles et techniques d'indexation.

**Auteurs:** Maghraoui Zied & Ben Ghorbel Mohamed Aziz  
**Date:** Janvier 2026  
**Contexte:** Cours SRI - Systèmes de Recherche d'Information

---

## 📁 Structure du projet

Ce repository contient deux travaux pratiques complets :

### 1. [TP Indexation](./tp_indexation/)
**Indexation et recherche d'information**

Implémentation complète d'un système d'indexation avec :
- Création et pré-traitement de corpus
- Construction d'index inversé
- Compression (Gap Encoding, Variable-Byte)
- Maintenance de l'index (ajout, suppression, mise à jour)
- Parallélisation avec ProcessPoolExecutor
- Comparaison avec Elasticsearch

**📄 Rapport:** [RAPPORT_TP_INDEXATION.md](./tp_indexation/RAPPORT_TP_INDEXATION.md)

### 2. [TP2 Modèles de Recherche](./tp2_modeles/)
**Comparaison de modèles de recherche d'information**

Implémentation et comparaison de quatre modèles de recherche :
- Modèle booléen
- Modèle vectoriel (TF-IDF)
- Modèle probabiliste (BM25)
- Modèle de langue

Évaluation avec **LLM as a Judge** (GPT-4o-mini).

**📄 Rapport:** [RAPPORT_COMPLET_TP2.md](./tp2_modeles/RAPPORT_COMPLET_TP2.md)

---

## 🚀 Installation rapide

### Prérequis
- Python 3.13+
- pip
- Docker (optionnel, pour Elasticsearch dans TP Indexation)

### Installation

#### TP Indexation
```bash
cd tp_indexation
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### TP2 Modèles
```bash
cd tp2_modeles
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📖 Utilisation

### TP Indexation

```bash
cd tp_indexation
source venv/bin/activate

# Partie 1: Corpus et Index
python partie1_corpus_et_index.py

# Partie 2: Compression et Maintenance
python partie2_compression_maintenance.py

# Partie 3: Elasticsearch (nécessite Docker)
docker run -d -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0
python partie3_elasticsearch.py

# Script principal
python main.py
```

### TP2 Modèles

```bash
cd tp2_modeles
source venv/bin/activate

# Configurer la clé API (optionnel)
export OPENAI_API_KEY=votre_cle
# ou créer un fichier .env avec OPENAI_API_KEY=votre_cle

# Exécuter les tests
python tp2_main.py

# Visualiser les résultats
python visualiser_resultats.py
```

---

## 📊 Résultats

### TP Indexation
- **Corpus 1** : 20 documents
- **Corpus 2** : 500 documents
- **Comparaison** : Performance avec/sans parallélisation, comparaison avec Elasticsearch
- **Rapport complet** : [RAPPORT_TP_INDEXATION.md](./tp_indexation/RAPPORT_TP_INDEXATION.md)

### TP2 Modèles
- **Corpus** : 50 documents répartis en 8 domaines
- **5 requêtes** testées
- **Évaluation LLM** : Scores de pertinence pour chaque modèle
- **Résultats** :
  - Vectoriel : 7.13/10 (meilleur score moyen)
  - BM25 : 7.13/10 (identique au vectoriel)
  - Booléen : 5.60/10 (3 victoires grâce à la précision)
  - Langue : 4.84/10 (rappel élevé, précision moyenne)
- **Rapport complet** : [RAPPORT_COMPLET_TP2.md](./tp2_modeles/RAPPORT_COMPLET_TP2.md)

---

## 🛠️ Technologies utilisées

### TP Indexation
- **Python 3.13**
- **NLTK** : Pré-traitement (tokenisation, stemming)
- **Elasticsearch 8.11.0** : Moteur de recherche distribué
- **Docker** : Conteneurisation d'Elasticsearch
- **multiprocessing** : Parallélisation

### TP2 Modèles
- **Python 3.13**
- **NLTK** : Pré-traitement
- **NumPy** : Calculs vectoriels
- **scikit-learn** : TF-IDF (référence)
- **OpenAI API** : LLM as a Judge (GPT-4o-mini)
- **Anthropic API** : Alternative LLM (optionnel)

---

## 📚 Documentation

### TP Indexation
- [README.md](./tp_indexation/README.md) : Documentation détaillée
- [DOCUMENTATION_CODE.md](./tp_indexation/DOCUMENTATION_CODE.md) : Documentation du code
- [RAPPORT_TP_INDEXATION.md](./tp_indexation/RAPPORT_TP_INDEXATION.md) : Rapport complet

### TP2 Modèles
- [README.md](./tp2_modeles/README.md) : Documentation détaillée
- [RAPPORT_COMPLET_TP2.md](./tp2_modeles/RAPPORT_COMPLET_TP2.md) : Rapport complet avec résultats

---

## 🔧 Configuration

### Variables d'environnement (TP2 Modèles)

Pour utiliser LLM as a Judge, configurer une clé API :

```bash
# Option 1: Variable d'environnement
export OPENAI_API_KEY=votre_cle

# Option 2: Fichier .env (dans tp2_modeles/)
echo "OPENAI_API_KEY=votre_cle" > tp2_modeles/.env
```

### Elasticsearch (TP Indexation)

```bash
# Démarrer Elasticsearch avec Docker
docker run -d -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0

# Vérifier que Elasticsearch fonctionne
curl http://localhost:9200
```

---

## 📝 Structure des fichiers

```
ri/
├── README.md                    # Ce fichier
├── .gitignore                   # Fichiers à ignorer
├── tp_indexation/               # TP Indexation
│   ├── README.md
│   ├── RAPPORT_TP_INDEXATION.md
│   ├── DOCUMENTATION_CODE.md
│   ├── partie1_corpus_et_index.py
│   ├── partie2_compression_maintenance.py
│   ├── partie3_elasticsearch.py
│   ├── main.py
│   ├── requirements.txt
│   └── ...
└── tp2_modeles/                 # TP2 Modèles
    ├── README.md
    ├── RAPPORT_COMPLET_TP2.md
    ├── tp2_main.py
    ├── modele_booleen.py
    ├── modele_vectoriel.py
    ├── modele_probabiliste.py
    ├── modele_langue.py
    ├── llm_judge.py
    ├── requirements.txt
    └── ...
```

---

## 🎯 Objectifs pédagogiques

### TP Indexation
- Comprendre les mécanismes d'indexation inversée
- Implémenter des techniques de compression
- Comparer avec des solutions industrielles (Elasticsearch)
- Mesurer l'impact de la parallélisation

### TP2 Modèles
- Implémenter les modèles fondamentaux de recherche
- Comprendre les différences entre les approches
- Utiliser LLM pour l'évaluation (approche moderne)
- Analyser les performances et les cas d'usage

---

## 📄 Licence

Ce projet est réalisé dans un contexte académique. Les fichiers de cours et les sujets de TP ne sont pas inclus dans ce repository.

---

## 👥 Auteurs

- **Maghraoui Zied**
- **Ben Ghorbel Mohamed Aziz**

---

## 🙏 Remerciements

- Professeurs du cours SRI
- Communauté open source (NLTK, Elasticsearch, OpenAI)

---

**Note:** Les environnements virtuels (`venv/`) et les fichiers générés (`*.json`, `*.pkl`, `corpus/`) sont exclus du repository via `.gitignore`.

