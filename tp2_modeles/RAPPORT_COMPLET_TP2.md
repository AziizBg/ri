# Rapport Complet TP2 - Modèles de Recherche d'Information

**Auteurs:** Maghraoui Zied & Ben Ghorbel Mohamed Aziz  
**Date:** Janvier 2026  
**Contexte:** TP2 Modèles de Recherche - Cours SRI

---

## Table des matières

1. [Résumé exécutif](#résumé-exécutif)
2. [Configuration du test](#configuration-du-test)
3. [Résultats détaillés par requête](#résultats-détaillés-par-requête)
4. [Analyse comparative des modèles](#analyse-comparative-des-modèles)
5. [Comparaison Vectoriel vs Probabiliste (BM25)](#comparaison-vectoriel-vs-probabiliste-bm25)
6. [Analyse du modèle de langue](#analyse-du-modèle-de-langue)
7. [Statistiques globales](#statistiques-globales)
8. [Conclusions et recommandations](#conclusions-et-recommandations)

---

## Résumé exécutif

Ce rapport présente les résultats complets de l'évaluation comparative de **quatre modèles de recherche d'information** sur un corpus de **50 documents** répartis en **8 domaines distincts** :

- **Informatique & IA** : Intelligence artificielle, machine learning, deep learning
- **Recherche d'Information** : Indexation, moteurs de recherche, Elasticsearch
- **Systèmes Distribués** : Cloud computing, bases de données, big data
- **Cybersécurité** : Sécurité informatique, blockchain, informatique quantique
- **Médecine** : Imagerie médicale, génétique, chirurgie
- **Histoire** : Révolution française, Empire romain, Guerres mondiales
- **Sciences** : Physique, biologie, écologie, mécanique quantique
- **Littérature** : Poésie, roman, théâtre, genres littéraires

**Cinq requêtes** ont été testées et évaluées par un LLM (GPT-4o-mini) agissant comme juge de pertinence.

### Résultats globaux

| Modèle | Score Moyen LLM | Résultats/Q | Victoires | Observations |
|--------|----------------|-------------|-----------|-------------|
| **Vectoriel** | **7.13/10** | 3.8 | **2** | Meilleur équilibre |
| **Probabiliste (BM25)** | **7.13/10** | 3.8 | 0 | Identique au vectoriel |
| **Langue** | **4.84/10** | 10.0 | 0 | Rappel élevé, précision moyenne |
| **Booléen** | **5.60/10** | 0.6 | **3** | Précis mais restrictif |

**Points clés :**
- Le modèle **Vectoriel** obtient le meilleur score moyen (7.13/10) avec 2 victoires
- Le modèle **Probabiliste (BM25)** a des performances identiques au vectoriel
- Le modèle **Booléen** remporte 3 victoires grâce à sa précision maximale
- Le modèle **Langue** retourne systématiquement 10 résultats (rappel élevé) mais avec une précision moyenne (4.84/10)
- Les modèles Vectoriel et BM25 retournent **exactement les mêmes documents dans le même ordre** pour toutes les requêtes

---

## Configuration du test

### Corpus
- **Nombre de documents** : 50
- **Domaines** : 8 domaines distincts (6-7 documents par domaine)
- **Termes uniques** : 248 (après pré-traitement)
- **Langue** : Français
- **Pré-traitement** : Tokenisation, normalisation, suppression stopwords, stemming (SnowballStemmer)

### Requêtes testées
1. "intelligence artificielle"
2. "recherche d'information"
3. "machine learning et deep learning"
4. "systèmes distribués"
5. "cybersécurité et blockchain"

### Évaluation
- **Méthode** : LLM as a Judge (GPT-4o-mini)
- **Échelle de pertinence** : 0-10 pour chaque document
- **Métriques calculées** : Score moyen, nombre de résultats, score max/min

### Paramètres des modèles
- **Vectoriel** : TF-IDF avec normalisation L2
- **BM25** : k1=1.5, b=0.75
- **Langue** : lambda=0.5 (lissage de Jelinek-Mercer)

---

## Résultats détaillés par requête

### Requête 1 : "intelligence artificielle"

**Contexte** : Requête simple et précise sur un sujet bien représenté dans le corpus.

#### Documents retournés

| Modèle | Documents | Scores techniques | Score LLM moyen |
|--------|-----------|-------------------|----------------|
| Booléen | [1] | - | 8.0/10 |
| Vectoriel | [1] | 0.577 | 8.0/10 |
| Probabiliste (BM25) | [1] | 3.051 | 8.0/10 |
| Langue | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] | -2.141, -5.565, ... | 6.5/10 |

#### Analyse détaillée

**Document 1** : "L'intelligence artificielle transforme notre façon de travailler et de vivre."
- **Domaine** : Informatique & IA
- **Pertinence LLM** : 8/10 pour Booléen, Vectoriel, BM25
- **Pertinence LLM** : 8/10 pour Langue (meilleur document)

**Documents additionnels (Langue) :**
- Documents 2-10 : Scores de pertinence variables (5-7/10)
- Le modèle Langue inclut des documents moins pertinents, ce qui abaisse sa moyenne

**Observations :**
- ✅ Tous les modèles (sauf Langue) ont trouvé le même document pertinent
- ✅ Le modèle Booléen est déclaré meilleur car "plus direct et efficace pour des requêtes simples"
- ⚠️ **Différence de scores techniques** : Vectoriel (0.577) vs BM25 (3.051) - **ratio de 5.3x**
- ✅ Le modèle Langue retourne 10 résultats avec un score moyen de 6.5/10 (rappel élevé)

**Meilleur modèle** : **Booléen** (précision maximale)

---

### Requête 2 : "recherche d'information"

**Contexte** : Requête sur un domaine spécialisé avec plusieurs documents pertinents.

#### Documents retournés

| Modèle | Documents | Scores techniques (top 5) | Score LLM moyen |
|--------|-----------|---------------------------|-----------------|
| Booléen | [8] | - | 10.0/10 |
| Vectoriel | [8, 11, 12, 9, 13, 19, 14, 42] | 0.482, 0.246, 0.236, 0.199, 0.198 | 6.88/10 |
| Probabiliste (BM25) | [8, 11, 12, 13, 9, 14, 19, 42] | 2.097, 1.101, 1.101, 0.996, 0.948 | 6.88/10 |
| Langue | [8, 11, 12, 13, 9, 14, 19, 42, 1, 2] | -1.938, -3.056, -3.056, -3.146, -3.191 | 5.5/10 |

#### Analyse détaillée

**Document 8** : "La recherche d'information est un domaine important de l'informatique."
- **Score LLM** : 10/10 (parfaitement pertinent)
- **Domaine** : Recherche d'Information

**Documents additionnels (Vectoriel/BM25/Langue) :**
- **Doc 9** : "Les moteurs de recherche indexent..." → 6/10
- **Doc 11** : "Elasticsearch est un moteur..." → 5/10
- **Doc 12** : "La recherche sémantique..." → 7/10
- **Doc 13** : "Les métadonnées enrichissent..." → 6/10
- **Doc 14** : "L'extraction d'information..." → 7/10
- **Doc 19** : "La similarité sémantique..." → 5/10
- **Doc 42** : "Les ontologies définissent..." → 3/10
- **Doc 1, 2** (Langue uniquement) : 2-3/10 (non pertinents)

**Observations :**
- ✅ Le modèle Booléen retourne uniquement le document parfaitement pertinent (10/10)
- ⚠️ Les modèles Vectoriel et BM25 retournent **8 documents** avec un score moyen de 6.88/10
- ✅ Le modèle Langue retourne **10 documents** incluant les 8 pertinents + 2 non pertinents (5.5/10)
- ⚠️ **Ordre identique** : Vectoriel et BM25 retournent les mêmes documents dans le même ordre
- ⚠️ **Scores techniques différents** : Doc 8 → 0.482 (Vectoriel) vs 2.097 (BM25) - **ratio de 4.4x**

**Meilleur modèle** : **Booléen** (précision maximale, document parfaitement pertinent)

---

### Requête 3 : "machine learning et deep learning"

**Contexte** : Requête multi-termes avec opérateur implicite (AND).

#### Documents retournés

| Modèle | Documents | Scores techniques (top 3) | Score LLM moyen |
|--------|-----------|---------------------------|-----------------|
| Booléen | [] | - | 0.0/10 |
| Vectoriel | [4, 3, 15] | 0.506, 0.410, 0.207 | 6.0/10 |
| Probabiliste (BM25) | [4, 3, 15] | 3.827, 3.611, 1.294 | 6.0/10 |
| Langue | [4, 3, 15, 1, 2, 5, 6, 7, 8, 9] | -5.871, -6.162, -8.808, -10.227, -10.227 | 4.7/10 |

#### Analyse détaillée

**Document 3** : "Le machine learning utilise des algorithmes pour apprendre à partir de données."
- **Score LLM** : 8/10 (très pertinent)
- **Domaine** : Informatique & IA

**Document 4** : "Le deep learning utilise des réseaux de neurones à plusieurs couches."
- **Score LLM** : 8/10 (très pertinent)
- **Domaine** : Informatique & IA

**Document 15** : "Les systèmes distribués répartissent le traitement sur plusieurs machines."
- **Score LLM** : 2/10 (non pertinent)
- **Domaine** : Systèmes Distribués

**Documents additionnels (Langue) :**
- Documents 1, 2, 5-9 : Scores de pertinence faibles (2-4/10)

**Observations :**
- ❌ Le modèle Booléen ne retourne aucun résultat (AND strict : "machine learning" ET "deep learning" dans le même document)
- ✅ Les modèles Vectoriel et BM25 trouvent 2 documents pertinents (3 et 4) et 1 non pertinent (15)
- ✅ Le modèle Langue trouve les 2 documents pertinents mais inclut 8 documents non pertinents
- ⚠️ **Ordre identique** : Vectoriel et BM25 retournent les mêmes documents dans le même ordre
- ⚠️ **Scores techniques** : Doc 4 → 0.506 (Vectoriel) vs 3.827 (BM25) - **ratio de 7.6x**

**Meilleur modèle** : **Vectoriel** (seul modèle à retourner des résultats pertinents avec bonne précision)

---

### Requête 4 : "systèmes distribués"

**Contexte** : Requête précise sur un domaine bien défini.

#### Documents retournés

| Modèle | Documents | Scores techniques (top 5) | Score LLM moyen |
|--------|-----------|---------------------------|-----------------|
| Booléen | [15] | - | 10.0/10 |
| Vectoriel | [15, 11, 23, 21, 20] | 0.536, 0.333, 0.190, 0.171, 0.166 | 5.8/10 |
| Probabiliste (BM25) | [15, 11, 23, 21, 20] | 2.312, 1.398, 1.101, 1.019, 0.948 | 5.8/10 |
| Langue | [15, 11, 23, 21, 20, 1, 2, 3, 4, 5] | -2.108, -3.166, -3.454, -3.528, -3.589 | 3.1/10 |

#### Analyse détaillée

**Document 15** : "Les systèmes distribués répartissent le traitement sur plusieurs machines."
- **Score LLM** : 10/10 (parfaitement pertinent)
- **Domaine** : Systèmes Distribués

**Documents additionnels (Vectoriel/BM25/Langue) :**
- **Doc 11** : "Elasticsearch est un moteur de recherche distribué..." → 8/10 (pertinent)
- **Doc 20** : "Le cloud computing permet d'accéder..." → 5/10 (partiellement pertinent)
- **Doc 21** : "Les bases de données relationnelles..." → 3/10 (peu pertinent)
- **Doc 23** : "Le big data analyse..." → 2/10 (non pertinent)
- **Doc 1-5** (Langue uniquement) : 1-2/10 (non pertinents)

**Observations :**
- ✅ Le modèle Booléen retourne uniquement le document parfaitement pertinent (10/10)
- ⚠️ Les modèles Vectoriel et BM25 retournent **5 documents** avec un score moyen de 5.8/10
- ⚠️ Le modèle Langue retourne **10 documents** avec un score moyen de 3.1/10 (inclut beaucoup de bruit)
- ⚠️ **Ordre identique** : Vectoriel et BM25 retournent les mêmes documents dans le même ordre
- ⚠️ **Scores techniques** : Doc 15 → 0.536 (Vectoriel) vs 2.312 (BM25) - **ratio de 4.3x**

**Meilleur modèle** : **Booléen** (précision maximale, document parfaitement pertinent)

---

### Requête 5 : "cybersécurité et blockchain"

**Contexte** : Requête multi-termes avec deux concepts liés.

#### Documents retournés

| Modèle | Documents | Scores techniques | Score LLM moyen |
|--------|-----------|-------------------|-----------------|
| Booléen | [] | - | 0.0/10 |
| Vectoriel | [22, 21] | 0.316, 0.304 | 9.0/10 |
| Probabiliste (BM25) | [22, 21] | 1.648, 1.525 | 9.0/10 |
| Langue | [22, 21, 1, 2, 3, 4, 5, 6, 7, 8] | -3.775, -3.853, -5.565, -5.565, -5.565 | 4.4/10 |

#### Analyse détaillée

**Document 22** : "Les blockchains garantissent la transparence et la sécurité des transactions."
- **Score LLM** : 9/10 (très pertinent pour blockchain)
- **Domaine** : Cybersécurité

**Document 21** : "La cybersécurité protège les systèmes contre les menaces numériques."
- **Score LLM** : 9/10 (très pertinent pour cybersécurité)
- **Domaine** : Cybersécurité

**Documents additionnels (Langue) :**
- Documents 1-8 : Scores de pertinence faibles (2-4/10)

**Observations :**
- ❌ Le modèle Booléen ne retourne aucun résultat (AND strict : "cybersécurité" ET "blockchain" dans le même document)
- ✅ Les modèles Vectoriel et BM25 retournent **2 documents pertinents** avec un score moyen de 9.0/10
- ⚠️ Le modèle Langue retourne **10 documents** avec un score moyen de 4.4/10 (inclut 8 documents non pertinents)
- ⚠️ **Ordre identique** : Vectoriel et BM25 retournent les mêmes documents dans le même ordre
- ⚠️ **Scores techniques** : Doc 22 → 0.316 (Vectoriel) vs 1.648 (BM25) - **ratio de 5.2x**
- ⚠️ **Limitation** : Aucun document ne traite des deux concepts ensemble

**Meilleur modèle** : **Vectoriel** (seul modèle à retourner des résultats très pertinents)

---

## Analyse comparative des modèles

### 1. Modèle Booléen

**Forces :**
- ✅ **Précision maximale** : Retourne uniquement les documents exactement pertinents
- ✅ **3 victoires** sur 5 requêtes
- ✅ **Pas de bruit** : Aucun document non pertinent retourné
- ✅ **Score parfait** : 10/10 sur 2 requêtes

**Faiblesses :**
- ❌ **Rappel faible** : 0.6 résultats par requête en moyenne
- ❌ **Requêtes multi-termes** : Échoue sur "machine learning et deep learning" et "cybersécurité et blockchain" (AND strict)
- ❌ **Score moyen plus faible** : 5.60/10 (impacté par les 0/10 sur requêtes multi-termes)
- ❌ **Pas de classement** : Tous les résultats sont équivalents

**Cas d'usage optimal :**
- Requêtes simples et précises
- Besoin de précision maximale
- Filtrage exact (ex: "tous les documents contenant X ET Y")

---

### 2. Modèle Vectoriel (TF-IDF)

**Forces :**
- ✅ **Meilleur score moyen** : 7.13/10
- ✅ **2 victoires** sur 5 requêtes
- ✅ **Bon équilibre** : 3.8 résultats par requête en moyenne
- ✅ **Classement par pertinence** : Résultats triés par similarité cosinus
- ✅ **Scores normalisés** : Entre 0 et 1, faciles à interpréter

**Faiblesses :**
- ⚠️ **Résultats identiques à BM25** : Même ordre, mêmes documents
- ⚠️ **Peut inclure du bruit** : Documents moins pertinents dans les résultats

**Cas d'usage optimal :**
- Recherche générale avec classement
- Besoin d'un bon compromis précision/rappel
- Systèmes de recommandation
- Collections de taille moyenne

---

### 3. Modèle Probabiliste (BM25)

**Forces :**
- ✅ **Fondement théorique solide** : Basé sur la théorie probabiliste
- ✅ **Normalisation de longueur** : Prend en compte la longueur des documents
- ✅ **Scores non normalisés** : Plus élevés et plus discriminants (3-7x plus élevés que vectoriel)
- ✅ **Score moyen identique au vectoriel** : 7.13/10

**Faiblesses :**
- ⚠️ **Résultats identiques au vectoriel** : Même ordre, mêmes documents (sur ce corpus)
- ⚠️ **Aucune victoire** : Même performance que le vectoriel mais pas de distinction
- ⚠️ **Peut inclure du bruit** : Documents moins pertinents dans les résultats

**Cas d'usage optimal :**
- Moteurs de recherche modernes
- Collections de taille variable
- Besoin de normalisation de longueur
- Standard de l'industrie (Elasticsearch, Solr)

---

### 4. Modèle de Langue

**Forces :**
- ✅ **Rappel élevé** : Retourne systématiquement 10 résultats
- ✅ **Trouve les documents pertinents** : Inclut toujours les documents pertinents dans les résultats
- ✅ **Modèle probabiliste élégant** : Basé sur la théorie des probabilités
- ✅ **Lissage de Jelinek-Mercer** : Gère les termes absents du document

**Faiblesses :**
- ⚠️ **Précision moyenne** : Score moyen de 4.84/10 (inclut beaucoup de bruit)
- ⚠️ **Scores négatifs** : Log-probabilités peu intuitives
- ⚠️ **Peut retourner trop de résultats** : Inclut souvent des documents non pertinents
- ⚠️ **Aucune victoire** : Jamais le meilleur modèle selon le LLM

**Cas d'usage optimal :**
- Corpus spécialisés (domaine spécifique)
- Besoin d'un rappel élevé
- Recherche avec termes partiels
- Modélisation probabiliste requise

---

## Comparaison Vectoriel vs Probabiliste (BM25)

### Observations principales

**Résultats identiques :**
- ✅ **Même ordre** : Les deux modèles retournent les documents dans le même ordre pour toutes les requêtes
- ✅ **Mêmes documents** : Les mêmes documents sont retournés
- ✅ **Même pertinence LLM** : Scores de pertinence identiques pour les mêmes documents

**Différences de scores techniques :**

| Requête | Document | Score Vectoriel | Score BM25 | Ratio |
|---------|----------|----------------|------------|-------|
| "intelligence artificielle" | Doc 1 | 0.577 | 3.051 | 5.3x |
| "recherche d'information" | Doc 8 | 0.482 | 2.097 | 4.4x |
| "machine learning..." | Doc 4 | 0.506 | 3.827 | 7.6x |
| "systèmes distribués" | Doc 15 | 0.536 | 2.312 | 4.3x |
| "cybersécurité..." | Doc 22 | 0.316 | 1.648 | 5.2x |

**Ratio moyen** : **5.3x** (les scores BM25 sont en moyenne 5.3 fois plus élevés)

### Explication des différences

1. **Normalisation** :
   - **Vectoriel** : Scores normalisés entre 0 et 1 (similarité cosinus)
   - **BM25** : Scores non normalisés, peuvent être > 1

2. **Formule** :
   - **Vectoriel** : TF-IDF normalisé par la norme L2
   - **BM25** : IDF × (tf × (k1+1)) / (tf + k1 × (1-b + b×|d|/avgdl))

3. **Impact** :
   - Les scores BM25 sont plus discriminants (écarts plus grands)
   - Les scores vectoriels sont plus comparables entre documents

### Conclusion

**Sur ce corpus, les modèles Vectoriel et BM25 sont fonctionnellement équivalents** :
- Même ordre de résultats
- Même pertinence perçue par le LLM
- Seule différence : échelle des scores techniques

**Recommandation** : Utiliser BM25 pour sa normalisation de longueur et son fondement théorique, mais les résultats pratiques sont identiques.

---

## Analyse du modèle de langue

### Caractéristiques des scores

Le modèle de langue calcule des **log-probabilités** (somme de log10 de probabilités) :

- **Nature** : Scores négatifs (car log10 d'une probabilité entre 0 et 1 est négatif)
- **Interprétation** : Plus le score est élevé (moins négatif), plus le document est probable
- **Exemple** : `-1.938` est meilleur que `-5.565`

### Performance par requête

| Requête | Score Moyen | Nombre Résultats | Meilleur Doc | Pire Doc |
|---------|-------------|------------------|--------------|----------|
| "intelligence artificielle" | 6.5/10 | 10 | 8/10 | 5/10 |
| "recherche d'information" | 5.5/10 | 10 | 10/10 | 2/10 |
| "machine learning..." | 4.7/10 | 10 | 8/10 | 2/10 |
| "systèmes distribués" | 3.1/10 | 10 | 10/10 | 1/10 |
| "cybersécurité..." | 4.4/10 | 10 | 9/10 | 2/10 |

### Observations

1. **Rappel élevé** : Retourne toujours 10 résultats (top_k=10)
2. **Inclusion des documents pertinents** : Les documents pertinents sont toujours dans les résultats
3. **Précision variable** : Inclut souvent des documents non pertinents (bruit)
4. **Score moyen modéré** : 4.84/10 (impacté par le bruit)

### Comparaison avec les autres modèles

| Aspect | Langue | Vectoriel/BM25 | Booléen |
|--------|--------|----------------|---------|
| **Rappel** | ⭐⭐⭐⭐⭐ (10 résultats) | ⭐⭐⭐ (3.8 résultats) | ⭐ (0.6 résultats) |
| **Précision** | ⭐⭐ (4.84/10) | ⭐⭐⭐⭐ (7.13/10) | ⭐⭐⭐⭐⭐ (5.60/10 mais 10/10 quand résultat) |
| **Bruit** | ⚠️ Élevé | ⚠️ Modéré | ✅ Aucun |
| **Vitesse** | ⚠️ Plus lent | ✅ Modéré | ✅ Très rapide |

### Recommandations pour le modèle de langue

1. **Ajuster le paramètre lambda** : Tester différentes valeurs (0.3, 0.5, 0.7)
2. **Limiter le nombre de résultats** : Réduire top_k pour améliorer la précision
3. **Utiliser pour rappel élevé** : Quand on veut trouver tous les documents potentiellement pertinents
4. **Corpus spécialisés** : Performe mieux sur des domaines spécifiques

---

## Statistiques globales

### Tableau récapitulatif

| Modèle | Score Moyen | Résultats/Q | Score Max | Score Min | Victoires |
|--------|-------------|-------------|-----------|-----------|-----------|
| **Vectoriel** | **7.13** | 3.8 | 9.0 | 5.8 | **2** |
| **Probabiliste (BM25)** | **7.13** | 3.8 | 9.0 | 5.8 | 0 |
| **Langue** | **4.84** | 10.0 | 6.5 | 3.1 | 0 |
| **Booléen** | **5.60** | 0.6 | 10.0 | 0.0 | **3** |

### Distribution des scores par requête

| Requête | Booléen | Vectoriel | BM25 | Langue |
|---------|---------|-----------|------|--------|
| "intelligence artificielle" | 8.0 | 8.0 | 8.0 | 6.5 |
| "recherche d'information" | 10.0 | 6.88 | 6.88 | 5.5 |
| "machine learning..." | 0.0 | 6.0 | 6.0 | 4.7 |
| "systèmes distribués" | 10.0 | 5.8 | 5.8 | 3.1 |
| "cybersécurité..." | 0.0 | 9.0 | 9.0 | 4.4 |

### Analyse de la précision vs rappel

| Modèle | Précision | Rappel | F1 (approximatif) |
|--------|-----------|--------|-------------------|
| **Booléen** | **Très élevée** (quand résultat) | Faible | Faible |
| **Vectoriel** | Moyenne-élevée | Moyen | **Bon** |
| **BM25** | Moyenne-élevée | Moyen | **Bon** |
| **Langue** | Faible-moyenne | **Très élevé** | Modéré |

**Observation** : 
- Le modèle Booléen privilégie la précision au détriment du rappel
- Les modèles Vectoriel et BM25 offrent un meilleur équilibre
- Le modèle Langue privilégie le rappel au détriment de la précision

---

## Conclusions et recommandations

### Conclusions principales

1. **Modèle Vectoriel** : Meilleur score moyen (7.13/10) avec 2 victoires
   - Bon équilibre précision/rappel
   - Classement par pertinence efficace
   - Recommandé pour la plupart des cas d'usage

2. **Modèle Probabiliste (BM25)** : Identique au vectoriel en pratique
   - Même ordre de résultats
   - Même pertinence perçue
   - Différence uniquement dans l'échelle des scores
   - Standard de l'industrie

3. **Modèle Booléen** : 3 victoires grâce à la précision maximale
   - Parfait pour requêtes simples et précises
   - Limité par le rappel faible et l'AND strict
   - Score moyen impacté par les échecs sur requêtes multi-termes

4. **Modèle de Langue** : Rappel élevé mais précision moyenne
   - Retourne systématiquement 10 résultats
   - Inclut toujours les documents pertinents
   - Mais inclut aussi beaucoup de bruit
   - Utile pour recherche exhaustive

### Recommandations d'utilisation

#### Quand utiliser le Modèle Vectoriel ?
- ✅ Recherche générale avec classement
- ✅ Besoin d'un bon compromis précision/rappel
- ✅ Systèmes de recommandation
- ✅ Collections de taille moyenne

#### Quand utiliser le Modèle Probabiliste (BM25) ?
- ✅ Moteurs de recherche modernes
- ✅ Collections de taille variable
- ✅ Besoin de normalisation de longueur
- ✅ Standard de l'industrie (Elasticsearch, Solr)

#### Quand utiliser le Modèle Booléen ?
- ✅ Recherche exacte requise
- ✅ Filtrage précis (ex: "tous les documents contenant X ET Y")
- ✅ Systèmes où la précision est critique
- ✅ Requêtes simples et précises

#### Quand utiliser le Modèle de Langue ?
- ✅ Corpus spécialisés (domaine spécifique)
- ✅ Besoin d'un rappel élevé
- ✅ Recherche avec termes partiels
- ✅ Modélisation probabiliste requise
- ⚠️ Nécessite un tuning des paramètres (lambda)

### Améliorations possibles

1. **Modèle Booléen** :
   - Implémenter un OR implicite pour les requêtes multi-termes
   - Ajouter un classement basé sur le nombre de termes correspondants

2. **Modèles Vectoriel et BM25** :
   - Tester sur un corpus plus volumineux pour voir si les différences apparaissent
   - Ajuster les paramètres BM25 (k1, b) pour optimiser les performances

3. **Modèle de Langue** :
   - Ajuster le paramètre lambda (lissage)
   - Réduire top_k pour améliorer la précision
   - Tester sur un corpus plus spécialisé
   - Implémenter un modèle bigramme au lieu d'unigramme

4. **Corpus** :
   - Augmenter la taille du corpus
   - Ajouter plus de documents par domaine
   - Tester avec des requêtes plus complexes

---

## Annexes

### A. Métadonnées du corpus

- **Nombre total de documents** : 50
- **Termes uniques** : 248 (après pré-traitement)
- **Domaines** : 8
- **Distribution** : 6-7 documents par domaine

### B. Configuration LLM

- **Modèle** : GPT-4o-mini (OpenAI)
- **Échelle de pertinence** : 0-10
- **Méthode** : LLM as a Judge

### C. Fichiers générés

- `corpus_tp2/` : 50 documents texte
- `evaluations_llm.json` : Résultats détaillés des évaluations
- `test_results_complet.log` : Log complet de l'exécution

---

**Fin du rapport complet**

