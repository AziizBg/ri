# TP2 - Modèles de Recherche d'Information

Ce projet implémente les différents modèles de recherche d'information vus en cours et utilise l'approche "LLM as a Judge" pour les comparer.

## Objectifs

1. Créer un corpus de documents
2. Implémenter les différents modèles :
   - Modèle booléen
   - Modèle vectoriel (TF-IDF)
   - Modèle probabiliste (BM25)
   - Modèle de langue
3. Utiliser LLM as a Judge pour comparer les modèles

## Structure du projet

```
tp2_modeles/
├── modele_booleen.py      # Modèle booléen
├── modele_vectoriel.py    # Modèle vectoriel (TF-IDF)
├── modele_probabiliste.py # Modèle probabiliste (BM25)
├── modele_langue.py       # Modèle de langue
├── llm_judge.py           # LLM as a Judge
├── tp2_main.py            # Script principal
├── requirements.txt        # Dépendances
└── README.md              # Ce fichier
```

## Installation

1. Installer les dépendances:
```bash
cd tp2_modeles
pip install -r requirements.txt
```

2. Configurer les clés API (optionnel, pour LLM as a Judge):
```bash
export OPENAI_API_KEY=votre_cle
# ou
export ANTHROPIC_API_KEY=votre_cle
```

## Utilisation

```bash
python tp2_main.py
```

## Modèles implémentés

### 1. Modèle Booléen
- Recherche exacte avec opérateurs AND, OR, NOT
- Pas de classement (tous les résultats sont équivalents)
- Simple et rapide

### 2. Modèle Vectoriel (TF-IDF)
- Représentation vectorielle des documents et requêtes
- Similarité cosinus
- Classement par pertinence

### 3. Modèle Probabiliste (BM25)
- Basé sur la théorie probabiliste
- Prend en compte la longueur des documents
- Paramètres k1 et b ajustables

### 4. Modèle de Langue
- Estime P(query|document)
- Lissage de Jelinek-Mercer
- Paramètre lambda ajustable

## LLM as a Judge

Le système utilise un LLM pour évaluer la pertinence des résultats retournés par chaque modèle. Le LLM :
- Évalue chaque document retourné (score 0-10)
- Compare les modèles
- Identifie le meilleur modèle pour chaque requête
- Fournit des justifications

## Résultats

Les résultats sont sauvegardés dans `evaluations_llm.json` avec :
- Scores par modèle et par requête
- Comparaisons détaillées
- Justifications des évaluations

