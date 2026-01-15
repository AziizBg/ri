# TP Indexation - Système de Recherche d'Information

Ce projet implémente les différentes parties du TP Indexation, couvrant la création d'un corpus, le pré-traitement, la construction d'un index inversé, la compression, la maintenance, la parallélisation, et la comparaison avec Elasticsearch.

## Structure du projet

```
tp_indexation/
├── partie1_corpus_et_index.py      # Partie 1: Corpus, pré-traitement, index inversé
├── partie2_compression_maintenance.py # Partie 2: Compression, maintenance, parallélisation
├── partie3_elasticsearch.py         # Partie 3: Elasticsearch et comparaison
├── requirements.txt                  # Dépendances Python
├── README.md                        # Ce fichier
├── corpus/                          # Dossier contenant les documents (généré)
└── index_inverse.json               # Index inversé sauvegardé (généré)
```

## Installation

1. Installer les dépendances:
```bash
pip install -r requirements.txt
```

2. Télécharger les ressources NLTK (fait automatiquement au premier lancement):
- Punkt tokenizer
- Stopwords (français et anglais)

3. Pour la Partie 3, démarrer Elasticsearch:
```bash
# Avec Docker
docker run -d -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0

# Ou installer Elasticsearch localement
```

## Utilisation

### Partie 1: Corpus et Index Inversé

```bash
python partie1_corpus_et_index.py
```

Cette partie:
- Crée un corpus de 20 documents textes
- Effectue le pré-traitement (tokenisation, normalisation, suppression stopwords, stemming)
- Construit l'index inversé
- Affiche les statistiques
- Teste la recherche

### Partie 2: Compression, Maintenance et Parallélisation

```bash
python partie2_compression_maintenance.py
```

Cette partie:
- Mesure les temps d'indexation séquentiel vs parallèle
- Compare les tailles mémoire avant/après compression
- Teste les opérations de maintenance (ajout, suppression, mise à jour)
- Discute les compromis espace/temps

### Partie 3: Elasticsearch

```bash
python partie3_elasticsearch.py
```

Cette partie:
- Crée un index Elasticsearch avec analyzer personnalisé
- Visualise les résultats de `_analyze`, `_segments`, et `_stats`
- Mesure les temps d'indexation avec 1, 2, et 4 shards
- Compare la taille disque avant/après `_forcemerge`
- Compare avec l'implémentation manuelle
- Discute comment Elasticsearch gère efficacement compression, maintenance et parallélisation

## Fonctionnalités implémentées

### Partie 1
- ✅ Création d'un corpus de 20 documents
- ✅ Pré-traitement complet (tokenisation, normalisation, stopwords, stemming)
- ✅ Construction de l'index inversé
- ✅ Recherche dans l'index
- ✅ Sauvegarde/chargement de l'index

### Partie 2
- ✅ Compression par gap encoding
- ✅ Compression variable-byte (structure)
- ✅ Maintenance de l'index (ajout, suppression, mise à jour)
- ✅ Parallélisation avec ProcessPoolExecutor
- ✅ Mesures de performance

### Partie 3
- ✅ Création d'index Elasticsearch avec analyzer personnalisé
- ✅ Analyse de texte avec `_analyze`
- ✅ Visualisation des segments avec `_segments`
- ✅ Statistiques avec `_stats`
- ✅ Force merge et mesure de la taille
- ✅ Comparaison avec implémentation manuelle

## Résultats attendus

### Partie 1
- Corpus de 20 documents créés dans `corpus/`
- Index inversé sauvegardé dans `index_inverse.json`
- Statistiques sur les termes et listes de postings

### Partie 2
- Rapport de performance montrant:
  - Accélération grâce à la parallélisation
  - Réduction de taille grâce à la compression
  - Temps des opérations de maintenance

### Partie 3
- Comparaison des temps d'indexation avec différents nombres de shards
- Analyse des fonctionnalités Elasticsearch
- Discussion des avantages/inconvénients

## Notes

- Le corpus est créé automatiquement avec des documents d'exemple en français
- Les stopwords français sont utilisés si disponibles, sinon anglais
- Elasticsearch doit être démarré pour exécuter la Partie 3
- Les résultats peuvent varier selon la machine et la charge système

## Auteur

Projet réalisé dans le cadre du cours de Système de Recherche d'Information (SRI).

