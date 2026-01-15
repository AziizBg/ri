# Documentation Technique Détaillée du Code - TP Indexation

**Auteurs:** Maghraoui Zied & Ben Ghorbel Mohamed Aziz  
**Date:** Janvier 2026  
**Version:** 1.0

---

## Table des matières

1. [Architecture Générale](#architecture-générale)
2. [Structure du Projet](#structure-du-projet)
3. [Partie 1 : Corpus et Index Inversé](#partie-1--corpus-et-index-inversé)
4. [Partie 2 : Compression, Maintenance et Parallélisation](#partie-2--compression-maintenance-et-parallélisation)
5. [Partie 3 : Elasticsearch](#partie-3--elasticsearch)
6. [Scripts Utilitaires](#scripts-utilitaires)
7. [Flux d'Exécution](#flux-dexécution)
8. [Structures de Données](#structures-de-données)
9. [Algorithmes Clés](#algorithmes-clés)

---

## Architecture Générale

Le projet est organisé en trois parties principales, chacune construite sur la précédente :

```
┌─────────────────────────────────────────────────────────┐
│                    main.py                              │
│  Point d'entrée - Gère l'exécution des 3 parties       │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Partie 1    │ │  Partie 2    │ │  Partie 3    │
│              │ │              │ │              │
│ - Corpus     │ │ - Compression│ │ - Elasticsearch│
│ - Pré-trait. │ │ - Maintenance│ │ - Comparaison │
│ - Index      │ │ - Parallélis.│ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌──────────────┐              ┌──────────────┐
│ Comparaison  │              │ Affichage    │
│ Corpus       │              │ Résultats    │
└──────────────┘              └──────────────┘
```

### Principes de Conception

1. **Modularité** : Chaque partie est indépendante et peut être exécutée séparément
2. **Réutilisabilité** : Les classes de la Partie 1 sont réutilisées dans les parties suivantes
3. **Extensibilité** : Facile d'ajouter de nouvelles méthodes de compression ou de recherche
4. **Séparation des responsabilités** : Chaque classe a un rôle bien défini

---

## Structure du Projet

### Fichiers Principaux

| Fichier | Rôle | Dépendances |
|---------|------|-------------|
| `main.py` | Point d'entrée, orchestration | Toutes les parties |
| `partie1_corpus_et_index.py` | Corpus, pré-traitement, index inversé | NLTK |
| `partie2_compression_maintenance.py` | Compression, maintenance, parallélisation | Partie 1 |
| `partie3_elasticsearch.py` | Intégration Elasticsearch | Partie 1, Elasticsearch |
| `comparaison_corpus.py` | Tests comparatifs | Toutes les parties |
| `afficher_resultats.py` | Visualisation des résultats | JSON |

### Dépendances Externes

- **NLTK** : Traitement du langage naturel (tokenisation, stopwords, stemming)
- **Elasticsearch** : Moteur de recherche distribué
- **Python Standard Library** : json, pickle, gzip, multiprocessing, concurrent.futures

---

## Partie 1 : Corpus et Index Inversé

### Fichier : `partie1_corpus_et_index.py`

#### 1.1 Classe `CorpusProcessor`

**Rôle** : Gère la création du corpus et le pré-traitement des documents.

##### Attributs

```python
self.language = 'french'          # Langue du corpus
self.stemmer = SnowballStemmer()  # Réducteur de mots à leur racine
self.stop_words = set()           # Mots vides à ignorer
self.documents = []               # Documents bruts
self.processed_documents = []     # Documents pré-traités
```

##### Méthode `__init__(self, language='french')`

**Fonction** : Initialise le processeur avec la langue spécifiée.

**Détails** :
- Crée un stemmer Snowball pour la langue (français par défaut)
- Charge les stopwords (mots vides) pour la langue
- Fallback sur l'anglais si le français n'est pas disponible
- Initialise les listes vides pour les documents

**Complexité** : O(1)

##### Méthode `create_corpus(self, num_docs=20)`

**Fonction** : Crée un corpus de documents et les sauvegarde dans des fichiers.

**Algorithme** :
1. Définit une liste de 20 documents d'exemple sur différents sujets informatiques
2. Crée le dossier `corpus/` s'il n'existe pas
3. Pour chaque document :
   - Génère un nom de fichier formaté (`doc_01.txt`, `doc_02.txt`, ...)
   - Écrit le contenu dans le fichier avec encodage UTF-8
   - Stocke les métadonnées (id, filename, text) dans `self.documents`

**Structure des documents** :
```python
{
    'id': 1,                           # Identifiant unique
    'filename': 'corpus/doc_01.txt',    # Chemin du fichier
    'text': 'Contenu textuel...'       # Texte brut
}
```

**Complexité** : O(n) où n = num_docs

##### Méthode `preprocess_text(self, text: str) -> List[str]`

**Fonction** : Pré-traite un texte pour l'indexation.

**Pipeline de pré-traitement** :

```
Texte brut
    ↓
1. Normalisation (minuscules)
    ↓
2. Suppression ponctuation
    ↓
3. Tokenisation
    ↓
4. Filtrage (stopwords + longueur)
    ↓
5. Stemming
    ↓
Liste de tokens
```

**Détails de chaque étape** :

1. **Normalisation** :
   ```python
   text = text.lower()
   ```
   - Convertit tout en minuscules pour l'uniformité
   - "Intelligence" et "intelligence" → même token

2. **Suppression ponctuation** :
   ```python
   text = re.sub(r'[^\w\s]', ' ', text)
   ```
   - Expression régulière : `[^\w\s]` = tout sauf lettres/chiffres/espaces
   - Remplace par un espace pour éviter la fusion de mots
   - Exemple : "l'intelligence" → "l intelligence"

3. **Tokenisation** :
   ```python
   tokens = word_tokenize(text, language='french')
   ```
   - Utilise NLTK pour découper en mots
   - Gère les apostrophes, contractions, etc.
   - Fallback sur `split()` si NLTK indisponible

4. **Filtrage** :
   ```python
   tokens = [t for t in tokens if t not in self.stop_words and len(t) > 2]
   ```
   - Supprime les stopwords (le, la, de, et, ...)
   - Supprime les tokens trop courts (≤ 2 caractères)
   - Exemple : "le", "de", "et" → supprimés

5. **Stemming** :
   ```python
   tokens = [self.stemmer.stem(token) for token in tokens]
   ```
   - Réduit les mots à leur racine
   - Exemple : "intelligence", "intelligent", "intelligemment" → "intellig"

**Exemple complet** :
```
Input:  "L'intelligence artificielle transforme notre société"
Step 1: "l'intelligence artificielle transforme notre société"
Step 2: "l intelligence artificielle transforme notre société"
Step 3: ["l", "intelligence", "artificielle", "transforme", "notre", "société"]
Step 4: ["intelligence", "artificielle", "transforme", "société"]
Step 5: ["intellig", "artificiel", "transform", "societ"]
```

**Complexité** : O(n) où n = longueur du texte

##### Méthode `preprocess_corpus(self)`

**Fonction** : Pré-traite tous les documents du corpus.

**Algorithme** :
```python
for doc in self.documents:
    processed_tokens = self.preprocess_text(doc['text'])
    self.processed_documents.append({
        'id': doc['id'],
        'tokens': processed_tokens
    })
```

**Structure des documents pré-traités** :
```python
{
    'id': 1,
    'tokens': ['intellig', 'artificiel', 'transform', 'societ']
}
```

**Complexité** : O(n × m) où n = nombre de documents, m = longueur moyenne des textes

#### 1.2 Classe `InvertedIndex`

**Rôle** : Construit et gère l'index inversé pour la recherche rapide.

##### Attributs

```python
self.index: Dict[str, Set[int]]  # terme → ensemble de doc_ids
self.doc_freq: Dict[str, int]    # terme → nombre de documents
```

**Structure de l'index inversé** :
```
{
    'intellig': {1, 5, 12},      # Le terme "intellig" apparaît dans les docs 1, 5, 12
    'artificiel': {1, 3},        # Le terme "artificiel" apparaît dans les docs 1, 3
    'recherch': {4, 7, 9},      # etc.
    ...
}
```

**Pourquoi des Sets ?**
- Évite les doublons (un terme peut apparaître plusieurs fois dans un document)
- Opérations d'intersection efficaces pour la recherche AND
- Complexité O(1) pour l'ajout et la vérification d'appartenance

##### Méthode `build_index(self, processed_documents: List[Dict])`

**Fonction** : Construit l'index inversé à partir des documents pré-traités.

**Algorithme** :
```python
for doc in processed_documents:
    doc_id = doc['id']
    tokens = doc['tokens']
    unique_tokens = set(tokens)  # Éliminer les doublons dans le document
    
    for token in unique_tokens:
        self.index[token].add(doc_id)  # Ajouter le doc_id à la liste de postings
        self.doc_freq[token] += 1      # Incrémenter la document frequency
```

**Exemple** :
```
Document 1: ['intellig', 'artificiel']
Document 2: ['recherch', 'informat']
Document 3: ['artificiel', 'recherch']

Après construction:
index = {
    'intellig': {1},
    'artificiel': {1, 3},
    'recherch': {2, 3},
    'informat': {2}
}
doc_freq = {
    'intellig': 1,
    'artificiel': 2,
    'recherch': 2,
    'informat': 1
}
```

**Complexité** : O(n × m) où n = nombre de documents, m = nombre moyen de termes uniques par document

##### Méthode `search(self, query: str, processor: CorpusProcessor) -> Set[int]`

**Fonction** : Recherche les documents contenant tous les termes de la requête (AND).

**Algorithme** :
```python
# 1. Pré-traiter la requête
query_tokens = processor.preprocess_text(query)

# 2. Récupérer la liste de postings du premier terme
result_docs = self.get_posting_list(query_tokens[0])

# 3. Intersection avec les listes de postings des autres termes
for token in query_tokens[1:]:
    result_docs = result_docs.intersection(self.get_posting_list(token))
```

**Exemple** :
```
Requête: "intelligence artificielle"
Tokens: ['intellig', 'artificiel']

Étape 1: result_docs = get_posting_list('intellig') = {1, 5, 12}
Étape 2: result_docs = {1, 5, 12} ∩ {1, 3} = {1}

Résultat: {1}  # Seul le document 1 contient les deux termes
```

**Pourquoi l'intersection ?**
- Recherche booléenne AND : tous les termes doivent être présents
- L'intersection de sets est optimisée en Python (O(min(len(set1), len(set2))))
- On commence par le terme avec la plus petite liste de postings pour optimiser

**Complexité** : O(k × m) où k = nombre de termes dans la requête, m = taille moyenne des listes de postings

##### Méthode `save_index(self, filename='index_inverse.json')`

**Fonction** : Sauvegarde l'index dans un fichier JSON.

**Transformation nécessaire** :
- JSON ne supporte pas les sets nativement
- Conversion : `Set[int]` → `List[int]` (triée pour la lisibilité)

```python
index_dict = {
    term: sorted(list(doc_ids)) 
    for term, doc_ids in self.index.items()
}
```

**Format JSON** :
```json
{
    "intellig": [1, 5, 12],
    "artificiel": [1, 3],
    ...
}
```

**Complexité** : O(n × m log m) où n = nombre de termes, m = taille moyenne des listes

##### Méthode `load_index(self, filename='index_inverse.json')`

**Fonction** : Charge l'index depuis un fichier JSON.

**Transformation** :
- `List[int]` → `Set[int]` pour restaurer la structure originale
- Recalcule `doc_freq` à partir des listes

**Complexité** : O(n × m) où n = nombre de termes, m = taille moyenne des listes

#### 1.3 Fonction `main()`

**Fonction** : Orchestre l'exécution de la Partie 1.

**Flux d'exécution** :
1. Créer le corpus (20 documents)
2. Pré-traiter tous les documents
3. Construire l'index inversé
4. Afficher les statistiques
5. Sauvegarder l'index
6. Tester la recherche avec quelques requêtes

---

## Partie 2 : Compression, Maintenance et Parallélisation

### Fichier : `partie2_compression_maintenance.py`

#### 2.1 Classe `CompressedIndex`

**Rôle** : Implémente des techniques de compression pour réduire la taille de l'index.

##### Méthode `compress_gap_encoding(self, doc_ids: List[int]) -> List[int]`

**Fonction** : Compresse une liste d'IDs de documents en utilisant le gap encoding.

**Principe** : Au lieu de stocker les valeurs absolues, on stocke les différences (gaps).

**Algorithme** :
```python
sorted_ids = sorted(doc_ids)  # [1, 3, 5, 7, 10]
gaps = [sorted_ids[0]]        # [1]  (première valeur absolue)

for i in range(1, len(sorted_ids)):
    gaps.append(sorted_ids[i] - sorted_ids[i-1])  # [1, 2, 2, 2, 3]
```

**Exemple** :
```
IDs originaux: [1, 3, 5, 7, 10]
IDs triés:     [1, 3, 5, 7, 10]
Gaps:          [1, 2, 2, 2, 3]

Décompression:
doc_ids = [1]                    # Premier gap = valeur absolue
doc_ids = [1, 1+2=3]             # 3
doc_ids = [1, 3, 3+2=5]          # 5
doc_ids = [1, 3, 5, 5+2=7]       # 7
doc_ids = [1, 3, 5, 7, 7+3=10]   # 10
```

**Avantages** :
- Les gaps sont généralement plus petits que les valeurs absolues
- Efficace pour les listes de postings triées et consécutives
- Réduction de 9-17% selon le corpus

**Complexité** : O(n log n) pour le tri + O(n) pour le calcul des gaps = O(n log n)

##### Méthode `decompress_gap_encoding(self, gaps: List[int]) -> List[int]`

**Fonction** : Décompresse une liste de gaps pour restaurer les IDs originaux.

**Algorithme** :
```python
doc_ids = [gaps[0]]  # Premier gap = valeur absolue

for i in range(1, len(gaps)):
    doc_ids.append(doc_ids[i-1] + gaps[i])
```

**Complexité** : O(n)

##### Méthode `compress_variable_byte(self, number: int) -> bytes`

**Fonction** : Compresse un entier en utilisant le variable-byte encoding.

**Principe** : Encoder un nombre sur un nombre variable d'octets (1-4 octets pour les entiers 32 bits).

**Structure d'un octet** :
```
Bit 7 (MSB): Bit de continuation (1 = octet suivant fait partie du nombre)
Bits 0-6:    7 bits de données
```

**Algorithme** :
```python
result = []
while number >= 128:  # Tant qu'il reste des bits à encoder
    result.append((number % 128) | 128)  # 7 bits de poids faible + bit de continuation
    number //= 128                        # Décaler de 7 bits
result.append(number % 128)  # Dernier octet (bit de continuation = 0)
```

**Exemple** :
```
Nombre: 300 (en binaire: 100101100)

Étape 1: 300 >= 128
    - 300 % 128 = 44 (00101100)
    - 44 | 128 = 172 (10101100) → octet 1
    - 300 // 128 = 2

Étape 2: 2 < 128
    - 2 % 128 = 2 (00000010) → octet 2

Résultat: [172, 2] = b'\xac\x02'

Décompression:
- Octet 1: 172 & 127 = 44, bit de continuation = 1 → continuer
- Octet 2: 2 & 127 = 2, bit de continuation = 0 → fin
- Nombre: 44 + (2 << 7) = 44 + 256 = 300
```

**Avantages** :
- Petits nombres (0-127) : 1 octet au lieu de 4
- Réduction significative pour les listes de petits gaps

**Complexité** : O(log n) où n = nombre à encoder

##### Méthode `compress_index(self, index: Dict[str, Set[int]], method='gap')`

**Fonction** : Compresse tout l'index en appliquant la méthode choisie.

**Algorithme** :
```python
for term, doc_ids in index.items():
    sorted_ids = sorted(list(doc_ids))
    if method == 'gap':
        self.index[term] = self.compress_gap_encoding(sorted_ids)
    else:
        self.index[term] = sorted_ids  # Pas de compression
```

**Complexité** : O(n × m log m) où n = nombre de termes, m = taille moyenne des listes

#### 2.2 Classe `IndexMaintenance`

**Rôle** : Gère les opérations de maintenance (ajout, suppression, mise à jour) sur l'index.

##### Méthode `add_document(self, doc_id: int, tokens: List[str])`

**Fonction** : Ajoute un nouveau document à l'index existant.

**Algorithme** :
```python
unique_tokens = set(tokens)  # Éliminer les doublons

for token in unique_tokens:
    self.index.index[token].add(doc_id)           # O(1) - ajout dans un set
    self.index.doc_freq[token] = self.index.doc_freq.get(token, 0) + 1
```

**Complexité** : O(k) où k = nombre de termes uniques dans le document
- Ajout dans un set : O(1) amorti
- Incrémentation : O(1)
- **Total : O(k)** - très rapide

**Exemple** :
```
Document 21: ['technolog', 'transform', 'societ']

Avant:
index = {'intellig': {1, 5}, 'recherch': {2, 3}}

Après:
index = {
    'intellig': {1, 5},
    'recherch': {2, 3},
    'technolog': {21},
    'transform': {21},
    'societ': {21}
}
```

##### Méthode `remove_document(self, doc_id: int)`

**Fonction** : Supprime un document de l'index.

**Algorithme** :
```python
terms_to_remove = []

# Parcourir tous les termes de l'index
for term, doc_ids in self.index.index.items():
    if doc_id in doc_ids:
        doc_ids.remove(doc_id)                    # O(1) - retrait d'un set
        self.index.doc_freq[term] -= 1
        
        if self.index.doc_freq[term] == 0:
            terms_to_remove.append(term)          # Terme n'apparaît plus nulle part

# Supprimer les termes orphelins
for term in terms_to_remove:
    del self.index.index[term]
    del self.index.doc_freq[term]
```

**Complexité** : O(n) où n = nombre total de termes dans l'index
- Doit parcourir tous les termes pour trouver ceux contenant le document
- **Plus coûteux que l'ajout** car nécessite un parcours complet

**Optimisation possible** :
- Maintenir un index inverse : `doc_id → set(terms)` pour O(k) au lieu de O(n)
- Trade-off : espace mémoire supplémentaire

##### Méthode `update_document(self, doc_id: int, new_tokens: List[str])`

**Fonction** : Met à jour un document (remplace son contenu).

**Implémentation** :
```python
self.remove_document(doc_id)  # Supprimer l'ancienne version
self.add_document(doc_id, new_tokens)  # Ajouter la nouvelle version
```

**Complexité** : O(n + k) où n = nombre de termes, k = nombre de nouveaux termes
- Coût de suppression + coût d'ajout

#### 2.3 Parallélisation

##### Fonction `process_document_batch(args)`

**Rôle** : Traite un batch de documents dans un processus séparé.

**Signature** :
```python
def process_document_batch(args) -> List[Dict]:
    doc_batch, language = args
    # ...
```

**Pourquoi une fonction globale ?**
- `ProcessPoolExecutor` nécessite des fonctions picklables (sérialisables)
- Les méthodes de classe ne sont pas directement picklables
- Solution : fonction globale qui crée un nouveau processeur

**Algorithme** :
```python
processor = CorpusProcessor(language=language)  # Nouveau processeur par processus
results = []

for doc in doc_batch:
    tokens = processor.preprocess_text(doc['text'])
    results.append({
        'id': doc['id'],
        'tokens': tokens
    })

return results
```

##### Classe `ParallelIndexBuilder`

**Rôle** : Construit l'index en parallèle en distribuant le travail sur plusieurs processus.

##### Méthode `build_index_parallel(self, documents: List[Dict], language='french')`

**Fonction** : Construit l'index en parallèle.

**Algorithme** :

1. **Division en batches** :
```python
batch_size = max(1, len(documents) // self.num_workers)
batches = []
for i in range(0, len(documents), batch_size):
    batches.append(documents[i:i+batch_size])
```

2. **Traitement parallèle** :
```python
with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
    results = list(executor.map(
        process_document_batch,
        [(batch, language) for batch in batches]
    ))
```

3. **Fusion des résultats** :
```python
processed_docs = []
for batch_results in results:
    processed_docs.extend(batch_results)
```

4. **Construction de l'index final** (séquentielle) :
```python
index = InvertedIndex()
index.build_index(processed_docs)
```

**Pourquoi ProcessPoolExecutor et pas ThreadPoolExecutor ?**
- Python a un GIL (Global Interpreter Lock) qui limite le vrai parallélisme avec les threads
- Les processus ont leur propre espace mémoire et contournent le GIL
- Vrai parallélisme CPU pour le pré-traitement (CPU-bound)

**Complexité** :
- Pré-traitement : O(n × m / p) où p = nombre de workers (parallélisé)
- Construction de l'index : O(n × m) (séquentielle, nécessaire)

**Overhead** :
- Communication inter-processus (pickle/unpickle)
- Création des processus
- Pour petits corpus : overhead > gain → plus lent
- Pour gros corpus : gain > overhead → plus rapide

#### 2.4 Fonction `measure_performance()`

**Fonction** : Mesure et compare les performances des différentes approches.

**Mesures effectuées** :

1. **Temps d'indexation séquentiel vs parallèle**
2. **Taille mémoire avant/après compression**
3. **Temps des opérations de maintenance**

**Méthodologie** :
- Utilise `time.time()` pour mesurer les temps
- Utilise `pickle.dumps()` pour estimer les tailles mémoire
- Répète les mesures pour obtenir des résultats fiables

---

## Partie 3 : Elasticsearch

### Fichier : `partie3_elasticsearch.py`

#### 3.1 Classe `ElasticsearchIndexer`

**Rôle** : Interface Python pour interagir avec Elasticsearch.

##### Méthode `__init__(self, host='localhost', port=9200)`

**Fonction** : Initialise le client Elasticsearch.

**Configuration** :
```python
self.es = Elasticsearch(
    [f'http://{host}:{port}'],
    verify_certs=False,        # Désactiver vérification SSL (dev)
    ssl_show_warn=False,       # Pas d'avertissements SSL
    request_timeout=30         # Timeout de 30 secondes
)
```

##### Méthode `create_index_with_custom_analyzer(self, num_shards=1)`

**Fonction** : Crée un index Elasticsearch avec un analyzer personnalisé.

**Structure de configuration** :

```python
settings = {
    "settings": {
        "number_of_shards": num_shards,      # Nombre de shards (parallélisation)
        "number_of_replicas": 0,              # Pas de réplication (dev)
        "analysis": {
            "analyzer": {
                "custom_french_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",   # Tokenisation standard
                    "filter": [
                        "lowercase",          # Minuscules
                        "french_stop",         # Stopwords français
                        "french_stemmer"       # Stemming français
                    ]
                }
            },
            "filter": {
                "french_stop": {
                    "type": "stop",
                    "stopwords": "_french_"   # Liste de stopwords français
                },
                "french_stemmer": {
                    "type": "stemmer",
                    "language": "french"      # Stemmer français
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "custom_french_analyzer",      # Pour l'indexation
                "search_analyzer": "custom_french_analyzer" # Pour la recherche
            },
            "doc_id": {
                "type": "integer"
            }
        }
    }
}
```

**Shards** :
- Un shard = une unité de distribution
- Plus de shards = meilleure parallélisation mais plus d'overhead
- Recommandation : 1 shard par 10-50 GB de données

##### Méthode `index_documents(self, documents: list)`

**Fonction** : Indexe les documents en utilisant l'API bulk.

**Préparation des actions** :
```python
actions = []
for doc in documents:
    action = {
        "_index": self.index_name,
        "_id": doc['id'],
        "_source": {
            "doc_id": doc['id'],
            "content": doc['text']
        }
    }
    actions.append(action)
```

**Indexation en masse** :
```python
success, failed = bulk(self.es, actions, chunk_size=100, request_timeout=30)
```

**Avantages du bulk** :
- Plus efficace que d'indexer un par un
- `chunk_size=100` : traite 100 documents par requête
- Réduit le nombre de round-trips réseau

##### Méthode `analyze_text(self, text: str)`

**Fonction** : Analyse un texte avec l'analyzer personnalisé.

**Utilisation** :
```python
result = self.es.indices.analyze(
    index=self.index_name,
    analyzer="custom_french_analyzer",
    text=text
)
```

**Résultat** :
```json
{
    "tokens": [
        {"token": "intellig", "position": 0},
        {"token": "artificiel", "position": 1},
        ...
    ]
}
```

**Utilité** : Déboguer et comprendre comment Elasticsearch traite le texte.

##### Méthode `get_segments_info(self)`

**Fonction** : Récupère les informations sur les segments de l'index.

**Segments** :
- Un segment = une unité de stockage dans Lucene (moteur d'Elasticsearch)
- Un index peut avoir plusieurs segments
- Les segments sont fusionnés (merged) périodiquement pour optimiser

**API** :
```python
stats = self.es.indices.segments(index=self.index_name)
```

##### Méthode `force_merge(self)`

**Fonction** : Force la fusion des segments en un seul.

**Utilisation** :
```python
self.es.indices.forcemerge(index=self.index_name, max_num_segments=1)
```

**Effets** :
- Réduit le nombre de segments
- Peut réduire la taille de l'index
- Améliore les performances de recherche
- **Coûteux** : opération I/O intensive

##### Méthode `search(self, query: str, size=10)`

**Fonction** : Recherche dans l'index avec une requête match.

**Requête** :
```python
query_body = {
    "query": {
        "match": {
            "content": query
        }
    }
}
```

**Résultat** :
- Documents correspondants avec scores de pertinence
- Triés par score décroissant
- Limité à `size` résultats

#### 3.2 Fonctions de Comparaison

##### `compare_indexation_times(num_shards_list=[1, 2, 4])`

**Fonction** : Compare les temps d'indexation avec différents nombres de shards.

**Méthodologie** :
1. Crée le corpus
2. Pour chaque nombre de shards :
   - Crée l'index avec ce nombre de shards
   - Mesure le temps d'indexation
   - Mesure la taille disque
3. Affiche les résultats comparatifs

##### `compare_with_manual_implementation()`

**Fonction** : Compare Elasticsearch avec l'implémentation manuelle.

**Comparaisons** :
- Temps d'indexation
- Taille mémoire/disque
- Analyse des différences

---

## Scripts Utilitaires

### Fichier : `comparaison_corpus.py`

**Rôle** : Compare les performances entre un corpus petit (20 docs) et volumineux (500 docs).

#### Fonction `generate_large_corpus(num_docs=500)`

**Fonction** : Génère un corpus volumineux avec des variations.

**Méthode** :
- Utilise une liste de 40+ sujets variés
- Utilise des templates de phrases
- Combine sujets et templates pour créer de la diversité
- Ajoute des variations conditionnelles

**Exemple** :
```python
topic = "intelligence artificielle"
sentence = "{} est un domaine important de l'informatique moderne."
text = sentence.format(topic)
# Résultat: "intelligence artificielle est un domaine important..."
```

#### Fonction `run_comparison_tests()`

**Fonction** : Exécute tous les tests de comparaison.

**Tests effectués** :
1. Indexation manuelle séquentielle (corpus 1 et 2)
2. Indexation manuelle parallèle (corpus 1 et 2)
3. Indexation Elasticsearch 1 shard (corpus 1 et 2)
4. Indexation Elasticsearch 4 shards (corpus 1 et 2)

**Résultats sauvegardés** :
- Fichier JSON : `resultats_comparaison.json`
- Format structuré pour analyse ultérieure

### Fichier : `afficher_resultats.py`

**Rôle** : Affiche les résultats de comparaison de manière formatée.

#### Fonction `afficher_resultats()`

**Fonction** : Lit et affiche les résultats de comparaison.

**Affichage** :
1. Tableau comparatif (métriques côte à côte)
2. Analyse des hypothèses (validation/invalidation)
3. Conclusion générale

**Format** :
- Tableaux alignés
- Calculs de ratios et améliorations
- Interprétation des résultats

### Fichier : `main.py`

**Rôle** : Point d'entrée principal du projet.

#### Fonction `main()`

**Fonction** : Gère l'exécution des différentes parties.

**Utilisation** :
```bash
python main.py 1    # Exécuter partie 1
python main.py 2    # Exécuter partie 2
python main.py 3    # Exécuter partie 3
python main.py 0    # Exécuter toutes les parties
```

**Implémentation** :
- Utilise `argparse` pour parser les arguments
- Appelle les fonctions `main()` de chaque partie
- Affiche des séparateurs visuels

---

## Flux d'Exécution

### Partie 1 : Corpus et Index Inversé

```
main.py
  │
  └─> partie1_corpus_et_index.py::main()
        │
        ├─> CorpusProcessor.__init__()
        │     └─> Initialise stemmer, stopwords
        │
        ├─> CorpusProcessor.create_corpus(20)
        │     ├─> Crée dossier corpus/
        │     ├─> Pour chaque document:
        │     │     ├─> Écrit fichier doc_XX.txt
        │     │     └─> Stocke métadonnées
        │     └─> Retourne liste de documents
        │
        ├─> CorpusProcessor.preprocess_corpus()
        │     └─> Pour chaque document:
        │           └─> CorpusProcessor.preprocess_text()
        │                 ├─> Normalisation (lowercase)
        │                 ├─> Suppression ponctuation
        │                 ├─> Tokenisation (NLTK)
        │                 ├─> Filtrage (stopwords, longueur)
        │                 └─> Stemming
        │
        ├─> InvertedIndex.__init__()
        │     └─> Initialise index et doc_freq
        │
        ├─> InvertedIndex.build_index(processed_docs)
        │     └─> Pour chaque document:
        │           └─> Pour chaque terme unique:
        │                 ├─> Ajoute doc_id à index[terme]
        │                 └─> Incrémente doc_freq[terme]
        │
        ├─> InvertedIndex.print_statistics()
        │     └─> Affiche stats (nb termes, fréquences, exemples)
        │
        ├─> InvertedIndex.save_index('index_inverse.json')
        │     └─> Convertit sets → listes, sauvegarde JSON
        │
        └─> Tests de recherche
              └─> InvertedIndex.search(query, processor)
                    ├─> Pré-traite la requête
                    └─> Intersection des listes de postings
```

### Partie 2 : Compression, Maintenance et Parallélisation

```
main.py
  │
  └─> partie2_compression_maintenance.py::main()
        │
        └─> measure_performance()
              │
              ├─> Création du corpus (réutilise Partie 1)
              │
              ├─> Mesure 1: Indexation séquentielle vs parallèle
              │     ├─> Séquentiel:
              │     │     ├─> CorpusProcessor.preprocess_corpus()
              │     │     └─> InvertedIndex.build_index()
              │     │
              │     └─> Parallèle:
              │           ├─> ParallelIndexBuilder.__init__(4)
              │           └─> ParallelIndexBuilder.build_index_parallel()
              │                 ├─> Divise documents en batches
              │                 ├─> ProcessPoolExecutor.map()
              │                 │     └─> process_document_batch() (parallèle)
              │                 ├─> Fusionne résultats
              │                 └─> InvertedIndex.build_index() (séquentiel)
              │
              ├─> Mesure 2: Compression
              │     ├─> Taille non compressée (pickle.dumps)
              │     ├─> CompressedIndex.compress_index(method='gap')
              │     │     └─> Pour chaque terme:
              │     │           └─> CompressedIndex.compress_gap_encoding()
              │     │                 ├─> Trie les IDs
              │     │                 └─> Calcule les gaps
              │     └─> Taille compressée
              │
              └─> Mesure 3: Maintenance
                    ├─> IndexMaintenance.add_document()
                    ├─> IndexMaintenance.remove_document()
                    └─> Mesure temps de chaque opération
```

### Partie 3 : Elasticsearch

```
main.py
  │
  └─> partie3_elasticsearch.py::main()
        │
        ├─> ElasticsearchIndexer.__init__()
        │     └─> Crée client Elasticsearch
        │
        ├─> ElasticsearchIndexer.check_connection()
        │     └─> Test ping()
        │
        ├─> compare_indexation_times([1, 2, 4])
        │     └─> Pour chaque nombre de shards:
        │           ├─> ElasticsearchIndexer.create_index_with_custom_analyzer()
        │           │     └─> es.indices.create() avec settings et mappings
        │           ├─> ElasticsearchIndexer.index_documents()
        │           │     ├─> Prépare actions bulk
        │           │     └─> bulk() avec chunk_size=100
        │           ├─> Mesure temps
        │           └─> ElasticsearchIndexer.get_index_size()
        │
        ├─> analyze_elasticsearch_features()
        │     ├─> ElasticsearchIndexer.analyze_text()
        │     ├─> ElasticsearchIndexer.get_segments_info()
        │     ├─> ElasticsearchIndexer.get_stats()
        │     └─> ElasticsearchIndexer.force_merge()
        │
        └─> compare_with_manual_implementation()
              ├─> Indexation manuelle (réutilise Partie 1)
              ├─> Indexation Elasticsearch
              └─> Comparaison temps et taille
```

---

## Structures de Données

### Document Brut

```python
{
    'id': int,              # Identifiant unique (1, 2, 3, ...)
    'filename': str,        # Chemin du fichier ('corpus/doc_01.txt')
    'text': str            # Contenu textuel brut
}
```

### Document Pré-traité

```python
{
    'id': int,             # Identifiant unique
    'tokens': List[str]    # Liste des tokens pré-traités
                          # Exemple: ['intellig', 'artificiel', 'transform']
}
```

### Index Inversé

```python
{
    'terme1': Set[int],   # Ensemble des doc_ids contenant le terme
    'terme2': Set[int],
    ...
}

# Exemple:
{
    'intellig': {1, 5, 12},
    'artificiel': {1, 3},
    'recherch': {4, 7, 9}
}
```

### Index Compressé (Gap Encoding)

```python
{
    'terme1': List[int],   # Liste de gaps au lieu de valeurs absolues
    'terme2': List[int],
    ...
}

# Exemple:
{
    'intellig': [1, 4, 7],      # IDs: [1, 5, 12] → gaps: [1, 4, 7]
    'artificiel': [1, 2],       # IDs: [1, 3] → gaps: [1, 2]
    'recherch': [4, 3, 2]       # IDs: [4, 7, 9] → gaps: [4, 3, 2]
}
```

### Document Frequency

```python
{
    'terme1': int,         # Nombre de documents contenant le terme
    'terme2': int,
    ...
}

# Exemple:
{
    'intellig': 3,         # Apparaît dans 3 documents
    'artificiel': 2,      # Apparaît dans 2 documents
    'recherch': 3         # Apparaît dans 3 documents
}
```

### Action Elasticsearch (Bulk)

```python
{
    "_index": "tp_indexation",
    "_id": 1,
    "_source": {
        "doc_id": 1,
        "content": "L'intelligence artificielle transforme..."
    }
}
```

---

## Algorithmes Clés

### 1. Pré-traitement de Texte

**Entrée** : Texte brut  
**Sortie** : Liste de tokens normalisés

**Étapes** :
1. Normalisation (lowercase)
2. Suppression ponctuation (regex)
3. Tokenisation (NLTK ou split)
4. Filtrage (stopwords + longueur)
5. Stemming (SnowballStemmer)

**Complexité** : O(n) où n = longueur du texte

### 2. Construction d'Index Inversé

**Entrée** : Liste de documents pré-traités  
**Sortie** : Index inversé (terme → set de doc_ids)

**Algorithme** :
```
Pour chaque document d:
    Pour chaque terme unique t dans d:
        index[t].add(d.id)
        doc_freq[t] += 1
```

**Complexité** : O(n × m) où n = nombre de documents, m = nombre moyen de termes par document

### 3. Recherche Booléenne AND

**Entrée** : Requête (texte)  
**Sortie** : Ensemble de doc_ids correspondants

**Algorithme** :
```
tokens = preprocess(query)
result = get_posting_list(tokens[0])

Pour chaque token t dans tokens[1:]:
    result = result ∩ get_posting_list(t)

Retourner result
```

**Optimisation** : Commencer par le terme avec la plus petite liste de postings

**Complexité** : O(k × m) où k = nombre de termes, m = taille moyenne des listes

### 4. Gap Encoding

**Entrée** : Liste d'IDs triés [1, 3, 5, 7, 10]  
**Sortie** : Liste de gaps [1, 2, 2, 2, 3]

**Algorithme** :
```
gaps = [ids[0]]
Pour i de 1 à len(ids)-1:
    gaps.append(ids[i] - ids[i-1])
```

**Décompression** :
```
ids = [gaps[0]]
Pour i de 1 à len(gaps)-1:
    ids.append(ids[i-1] + gaps[i])
```

**Complexité** : O(n) pour compression et décompression

### 5. Indexation Parallèle

**Entrée** : Liste de documents bruts  
**Sortie** : Index inversé

**Algorithme** :
```
1. Diviser documents en batches (batch_size = n / num_workers)
2. Traiter chaque batch en parallèle (ProcessPoolExecutor):
   - Pré-traiter les documents du batch
   - Retourner documents pré-traités
3. Fusionner tous les résultats
4. Construire l'index final (séquentiel)
```

**Complexité** :
- Pré-traitement : O(n × m / p) où p = nombre de workers
- Construction index : O(n × m) (séquentiel)

---

## Conclusion

Ce document a fourni une explication technique détaillée de tous les composants du code du TP Indexation. Chaque classe, méthode, algorithme et structure de données a été expliqué avec :

- **Rôle et responsabilité**
- **Algorithme détaillé**
- **Complexité temporelle**
- **Exemples concrets**
- **Justifications des choix de conception**

Le code est organisé de manière modulaire et extensible, permettant une compréhension claire et une maintenance facile. Les trois parties s'appuient les unes sur les autres tout en restant indépendantes, ce qui facilite les tests et le développement.

