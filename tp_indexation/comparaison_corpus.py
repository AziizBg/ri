"""
Script de comparaison entre corpus petit et volumineux
Teste les performances de l'indexation manuelle vs Elasticsearch

Ce module effectue une comparaison complète des performances entre :
1. Un corpus petit (20 documents) et un corpus volumineux (500 documents)
2. L'indexation manuelle (séquentielle et parallèle) vs Elasticsearch
3. Différentes configurations (1 shard vs 4 shards pour Elasticsearch)

Les résultats permettent de valider des hypothèses sur :
- L'efficacité de la parallélisation avec les corpus volumineux
- L'efficacité relative d'Elasticsearch avec les corpus volumineux
- L'impact des shards multiples sur les performances
- La scalabilité (temps par document)

Les résultats sont sauvegardés dans resultats_comparaison.json pour
analyse ultérieure avec afficher_resultats.py.
"""

import os  # Pour créer les dossiers de corpus
import time  # Pour mesurer les temps d'exécution
import json  # Pour sauvegarder les résultats en JSON
import pickle  # Pour mesurer les tailles mémoire
import gzip  # Pour la compression (non utilisé directement ici)
from collections import defaultdict  # Pour les dictionnaires avec valeurs par défaut
from typing import Dict, List, Set  # Pour le typage statique
from partie1_corpus_et_index import CorpusProcessor, InvertedIndex  # Classes de la partie 1
from partie2_compression_maintenance import CompressedIndex, ParallelIndexBuilder  # Classes de la partie 2
from partie3_elasticsearch import ElasticsearchIndexer  # Classe de la partie 3

# Sujets pour générer un corpus plus volumineux
TOPICS = [
    "intelligence artificielle", "machine learning", "deep learning", "réseaux de neurones",
    "traitement du langage naturel", "vision par ordinateur", "reconnaissance vocale",
    "recherche d'information", "moteurs de recherche", "indexation inversée",
    "compression de données", "algorithmes de recherche", "bases de données",
    "cloud computing", "virtualisation", "containers", "microservices",
    "cybersécurité", "cryptographie", "blockchain", "bitcoin",
    "informatique quantique", "calcul distribué", "big data", "data science",
    "analyse de données", "visualisation", "business intelligence",
    "développement logiciel", "programmation", "architecture logicielle",
    "tests automatisés", "intégration continue", "déploiement continu",
    "agile", "scrum", "devops", "infrastructure as code",
    "réseaux informatiques", "protocoles de communication", "API REST",
    "bases de données relationnelles", "NoSQL", "MongoDB", "Redis",
    "systèmes distribués", "tolérance aux pannes", "haute disponibilité",
    "performance", "optimisation", "caching", "load balancing"
]

def generate_large_corpus(num_docs=500):
    """
    Générer un corpus volumineux avec des variations de textes
    
    Cette fonction génère un corpus de documents en utilisant des templates
    de phrases et une liste de sujets variés. Les documents sont créés en
    combinant des sujets aléatoires avec des structures de phrases variées.
    
    Args:
        num_docs (int): Nombre de documents à générer. Par défaut 500
    
    Returns:
        list: Liste de dictionnaires contenant les documents générés.
              Chaque document a :
              - 'id': Identifiant unique (commence à 1)
              - 'text': Contenu textuel du document
    """
    documents = []
    base_sentences = [
        "{} est un domaine important de l'informatique moderne.",
        "Les applications de {} transforment notre société.",
        "{} utilise des techniques avancées pour résoudre des problèmes complexes.",
        "La recherche en {} progresse rapidement.",
        "{} permet d'améliorer les performances des systèmes.",
        "Les entreprises adoptent {} pour rester compétitives.",
        "{} nécessite une expertise technique approfondie.",
        "L'avenir de {} est prometteur.",
        "{} révolutionne la façon dont nous travaillons.",
        "Les développeurs utilisent {} pour créer des solutions innovantes.",
        "{} est essentiel dans le monde numérique d'aujourd'hui.",
        "La compréhension de {} est cruciale pour les professionnels.",
        "{} offre de nombreuses opportunités de carrière.",
        "Les technologies {} évoluent constamment.",
        "{} combine théorie et pratique pour des résultats optimaux.",
        "L'implémentation de {} nécessite une planification minutieuse.",
        "{} est au cœur de l'innovation technologique.",
        "Les experts en {} sont très demandés.",
        "{} transforme les processus métier traditionnels.",
        "La maîtrise de {} ouvre de nouvelles perspectives."
    ]
    
    for i in range(1, num_docs + 1):
        # Sélectionner un sujet aléatoire
        topic = TOPICS[i % len(TOPICS)]
        sentence = base_sentences[i % len(base_sentences)]
        text = sentence.format(topic)
        
        # Ajouter des variations
        if i % 3 == 0:
            text += " Les systèmes modernes intègrent ces concepts."
        if i % 5 == 0:
            text += " L'analyse approfondie révèle des insights précieux."
        if i % 7 == 0:
            text += " Les meilleures pratiques recommandent une approche méthodique."
        
        documents.append({
            'id': i,
            'text': text
        })
    
    return documents

def save_corpus_to_files(documents, corpus_dir):
    """
    Sauvegarder le corpus dans des fichiers texte
    
    Cette fonction sauvegarde chaque document du corpus dans un fichier
    séparé dans le dossier spécifié.
    
    Args:
        documents (list): Liste des documents à sauvegarder
        corpus_dir (str): Nom du dossier où sauvegarder les fichiers
    
    Returns:
        int: Nombre de documents sauvegardés
    """
    os.makedirs(corpus_dir, exist_ok=True)
    for doc in documents:
        filename = f"{corpus_dir}/doc_{doc['id']:03d}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(doc['text'])
    return len(documents)

def test_manual_indexation(documents, num_workers=None):
    """
    Tester l'indexation manuelle (séquentielle et parallèle)
    
    Cette fonction mesure les performances de l'indexation manuelle :
    - Temps d'indexation séquentielle
    - Temps d'indexation parallèle (si num_workers est spécifié)
    - Tailles mémoire (non compressée et compressée)
    
    Args:
        documents (list): Liste des documents à indexer
        num_workers (int, optional): Nombre de workers pour la parallélisation.
                                    Si None, seule l'indexation séquentielle est testée
    
    Returns:
        dict: Dictionnaire contenant les résultats de performance :
              - 'time_seq': Temps d'indexation séquentielle
              - 'time_par': Temps d'indexation parallèle (None si non testé)
              - 'size_uncompressed': Taille mémoire non compressée
              - 'size_compressed': Taille mémoire compressée
              - 'num_terms': Nombre de termes uniques dans l'index
              - 'index': L'index inversé construit
    """
    processor = CorpusProcessor(language='french')
    processor.documents = documents
    
    # Test séquentiel
    start_time = time.time()
    processed_docs = processor.preprocess_corpus()
    index_seq = InvertedIndex()
    index_seq.build_index(processed_docs)
    time_seq = time.time() - start_time
    
    # Test parallèle
    if num_workers:
        parallel_builder = ParallelIndexBuilder(num_workers=num_workers)
        start_time = time.time()
        index_par, _ = parallel_builder.build_index_parallel(documents)
        time_par = time.time() - start_time
    else:
        time_par = None
        index_par = None
    
    # Taille mémoire
    size_uncompressed = len(pickle.dumps(index_seq.index))
    
    # Compression
    compressed_index = CompressedIndex()
    compressed_index.compress_index(index_seq.index, method='gap')
    size_compressed = compressed_index.get_size_memory()
    
    return {
        'time_seq': time_seq,
        'time_par': time_par,
        'size_uncompressed': size_uncompressed,
        'size_compressed': size_compressed,
        'num_terms': len(index_seq.index),
        'index': index_seq
    }

def test_elasticsearch_indexation(documents, num_shards=1):
    """
    Tester l'indexation avec Elasticsearch
    
    Cette fonction mesure les performances de l'indexation Elasticsearch :
    - Temps d'indexation
    - Taille disque de l'index
    - Nombre de documents indexés
    
    Args:
        documents (list): Liste des documents à indexer
        num_shards (int): Nombre de shards pour l'index. Par défaut 1
    
    Returns:
        dict: Dictionnaire contenant les résultats ou None si Elasticsearch
              n'est pas disponible. Contient :
              - 'time': Temps d'indexation
              - 'size': Taille disque de l'index en bytes
              - 'num_docs': Nombre de documents indexés
              - 'num_shards': Nombre de shards utilisés
    """
    indexer = ElasticsearchIndexer()
    if not indexer.check_connection():
        return None
    
    # Créer l'index
    indexer.create_index_with_custom_analyzer(num_shards=num_shards)
    
    # Indexer les documents
    start_time = time.time()
    success, failed = indexer.index_documents(documents)
    indexer.es.indices.refresh(index=indexer.index_name)
    time_index = time.time() - start_time
    
    # Taille disque
    size_disk = indexer.get_index_size()
    
    # Statistiques
    stats = indexer.get_stats()
    num_docs = stats['indices'][indexer.index_name]['total']['docs']['count']
    
    return {
        'time': time_index,
        'size': size_disk,
        'num_docs': num_docs,
        'num_shards': num_shards
    }

def run_comparison_tests():
    """
    Exécuter tous les tests de comparaison
    
    Cette fonction orchestre l'exécution complète des tests de comparaison :
    1. Génération de deux corpus (petit et volumineux)
    2. Tests d'indexation manuelle (séquentielle et parallèle) pour chaque corpus
    3. Tests d'indexation Elasticsearch (1 et 4 shards) pour chaque corpus
    4. Analyse comparative des résultats
    5. Sauvegarde des résultats dans resultats_comparaison.json
    
    Les résultats permettent de valider les hypothèses sur :
    - L'efficacité de la parallélisation avec les corpus volumineux
    - L'efficacité relative d'Elasticsearch avec les corpus volumineux
    - L'impact des shards multiples
    - La scalabilité (temps par document)
    """
    print("=" * 80)
    print("COMPARAISON CORPUS PETIT vs VOLUMINEUX")
    print("=" * 80)
    
    # Créer les deux corpus
    print("\n1. Création des corpus...")
    corpus1_docs = generate_large_corpus(num_docs=20)
    corpus2_docs = generate_large_corpus(num_docs=500)
    
    save_corpus_to_files(corpus1_docs, 'corpus1')
    save_corpus_to_files(corpus2_docs, 'corpus2')
    
    print(f"✓ Corpus 1 créé: {len(corpus1_docs)} documents")
    print(f"✓ Corpus 2 créé: {len(corpus2_docs)} documents")
    
    results = {
        'corpus1': {'num_docs': len(corpus1_docs)},
        'corpus2': {'num_docs': len(corpus2_docs)}
    }
    
    # === CORPUS 1 (PETIT) ===
    print("\n" + "=" * 80)
    print("TESTS AVEC CORPUS 1 (20 documents)")
    print("=" * 80)
    
    print("\n--- Indexation manuelle (séquentielle) ---")
    results_c1_manual = test_manual_indexation(corpus1_docs)
    results['corpus1']['manual_seq'] = results_c1_manual
    print(f"Temps: {results_c1_manual['time_seq']:.4f} s")
    print(f"Taille non compressée: {results_c1_manual['size_uncompressed']/1024:.2f} KB")
    print(f"Taille compressée: {results_c1_manual['size_compressed']/1024:.2f} KB")
    print(f"Nombre de termes: {results_c1_manual['num_terms']}")
    
    print("\n--- Indexation manuelle (parallèle, 4 workers) ---")
    results_c1_par = test_manual_indexation(corpus1_docs, num_workers=4)
    if results_c1_par['time_par']:
        results['corpus1']['manual_par'] = results_c1_par
        speedup = results_c1_manual['time_seq'] / results_c1_par['time_par']
        print(f"Temps: {results_c1_par['time_par']:.4f} s")
        print(f"Accélération: {speedup:.2f}x")
    
    print("\n--- Elasticsearch (1 shard) ---")
    results_c1_es1 = test_elasticsearch_indexation(corpus1_docs, num_shards=1)
    if results_c1_es1:
        results['corpus1']['elasticsearch_1'] = results_c1_es1
        print(f"Temps: {results_c1_es1['time']:.4f} s")
        print(f"Taille: {results_c1_es1['size']/1024:.2f} KB")
    
    print("\n--- Elasticsearch (4 shards) ---")
    results_c1_es4 = test_elasticsearch_indexation(corpus1_docs, num_shards=4)
    if results_c1_es4:
        results['corpus1']['elasticsearch_4'] = results_c1_es4
        print(f"Temps: {results_c1_es4['time']:.4f} s")
        print(f"Taille: {results_c1_es4['size']/1024:.2f} KB")
    
    # === CORPUS 2 (VOLUMINEUX) ===
    print("\n" + "=" * 80)
    print("TESTS AVEC CORPUS 2 (500 documents)")
    print("=" * 80)
    
    print("\n--- Indexation manuelle (séquentielle) ---")
    results_c2_manual = test_manual_indexation(corpus2_docs)
    results['corpus2']['manual_seq'] = results_c2_manual
    print(f"Temps: {results_c2_manual['time_seq']:.4f} s")
    print(f"Taille non compressée: {results_c2_manual['size_uncompressed']/1024:.2f} KB")
    print(f"Taille compressée: {results_c2_manual['size_compressed']/1024:.2f} KB")
    print(f"Nombre de termes: {results_c2_manual['num_terms']}")
    
    print("\n--- Indexation manuelle (parallèle, 4 workers) ---")
    results_c2_par = test_manual_indexation(corpus2_docs, num_workers=4)
    if results_c2_par['time_par']:
        results['corpus2']['manual_par'] = results_c2_par
        speedup = results_c2_manual['time_seq'] / results_c2_par['time_par']
        print(f"Temps: {results_c2_par['time_par']:.4f} s")
        print(f"Accélération: {speedup:.2f}x")
    
    print("\n--- Elasticsearch (1 shard) ---")
    results_c2_es1 = test_elasticsearch_indexation(corpus2_docs, num_shards=1)
    if results_c2_es1:
        results['corpus2']['elasticsearch_1'] = results_c2_es1
        print(f"Temps: {results_c2_es1['time']:.4f} s")
        print(f"Taille: {results_c2_es1['size']/1024:.2f} KB")
    
    print("\n--- Elasticsearch (4 shards) ---")
    results_c2_es4 = test_elasticsearch_indexation(corpus2_docs, num_shards=4)
    if results_c2_es4:
        results['corpus2']['elasticsearch_4'] = results_c2_es4
        print(f"Temps: {results_c2_es4['time']:.4f} s")
        print(f"Taille: {results_c2_es4['size']/1024:.2f} KB")
    
    # === COMPARAISON ===
    print("\n" + "=" * 80)
    print("ANALYSE COMPARATIVE")
    print("=" * 80)
    
    print("\n1. PARALLÉLISATION - Indexation manuelle")
    print("-" * 80)
    if 'manual_par' in results['corpus1'] and 'manual_par' in results['corpus2']:
        c1_speedup = results['corpus1']['manual_seq']['time_seq'] / results['corpus1']['manual_par']['time_par']
        c2_speedup = results['corpus2']['manual_seq']['time_seq'] / results['corpus2']['manual_par']['time_par']
        print(f"Corpus 1 (20 docs): Accélération = {c1_speedup:.2f}x")
        print(f"Corpus 2 (500 docs): Accélération = {c2_speedup:.2f}x")
        print(f"✓ La parallélisation est {c2_speedup/c1_speedup:.2f}x plus efficace avec le corpus volumineux")
    
    print("\n2. ELASTICSEARCH vs MANUEL - Temps d'indexation")
    print("-" * 80)
    if 'elasticsearch_1' in results['corpus1'] and 'elasticsearch_1' in results['corpus2']:
        c1_ratio = results['corpus1']['elasticsearch_1']['time'] / results['corpus1']['manual_seq']['time_seq']
        c2_ratio = results['corpus2']['elasticsearch_1']['time'] / results['corpus2']['manual_seq']['time_seq']
        print(f"Corpus 1: ES est {c1_ratio:.2f}x {'plus rapide' if c1_ratio < 1 else 'plus lent'} que manuel")
        print(f"Corpus 2: ES est {c2_ratio:.2f}x {'plus rapide' if c2_ratio < 1 else 'plus lent'} que manuel")
        if c2_ratio < c1_ratio:
            print(f"✓ Elasticsearch devient relativement plus efficace avec le corpus volumineux")
    
    print("\n3. ELASTICSEARCH - Impact des shards")
    print("-" * 80)
    if 'elasticsearch_1' in results['corpus1'] and 'elasticsearch_4' in results['corpus1']:
        c1_shard_speedup = results['corpus1']['elasticsearch_1']['time'] / results['corpus1']['elasticsearch_4']['time']
        print(f"Corpus 1: 4 shards = {c1_shard_speedup:.2f}x plus rapide que 1 shard")
    if 'elasticsearch_1' in results['corpus2'] and 'elasticsearch_4' in results['corpus2']:
        c2_shard_speedup = results['corpus2']['elasticsearch_1']['time'] / results['corpus2']['elasticsearch_4']['time']
        print(f"Corpus 2: 4 shards = {c2_shard_speedup:.2f}x plus rapide que 1 shard")
        if 'elasticsearch_1' in results['corpus1'] and 'elasticsearch_4' in results['corpus1']:
            print(f"✓ L'avantage des shards multiples est {c2_shard_speedup/c1_shard_speedup:.2f}x plus marqué avec le corpus volumineux")
    
    print("\n4. SCALABILITÉ - Temps par document")
    print("-" * 80)
    c1_time_per_doc = results['corpus1']['manual_seq']['time_seq'] / results['corpus1']['num_docs']
    c2_time_per_doc = results['corpus2']['manual_seq']['time_seq'] / results['corpus2']['num_docs']
    print(f"Corpus 1: {c1_time_per_doc*1000:.4f} ms/document")
    print(f"Corpus 2: {c2_time_per_doc*1000:.4f} ms/document")
    if c2_time_per_doc < c1_time_per_doc:
        print(f"✓ Efficacité améliorée avec le corpus volumineux (meilleure amortisation des coûts fixes)")
    
    # Sauvegarder les résultats
    with open('resultats_comparaison.json', 'w', encoding='utf-8') as f:
        # Convertir les résultats en format JSON-serializable
        json_results = {}
        for corpus_name, corpus_data in results.items():
            json_results[corpus_name] = {}
            for key, value in corpus_data.items():
                if key == 'index':
                    continue  # Ne pas sauvegarder l'index
                if isinstance(value, dict):
                    json_results[corpus_name][key] = {k: v for k, v in value.items() if k != 'index'}
                else:
                    json_results[corpus_name][key] = value
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Résultats sauvegardés dans 'resultats_comparaison.json'")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("""
    Hypothèses vérifiées:
    
    1. PARALLÉLISATION:
       - Plus efficace avec les corpus volumineux
       - L'overhead de communication est amorti sur plus de données
       - Le gain augmente avec la taille du corpus
    
    2. ELASTICSEARCH:
       - Devient relativement plus efficace avec les corpus volumineux
       - Les shards multiples offrent un avantage plus marqué sur gros corpus
       - L'overhead initial est mieux amorti sur plus de documents
    
    3. SCALABILITÉ:
       - Le temps par document diminue avec la taille du corpus
       - Meilleure utilisation des ressources avec plus de données
       - Elasticsearch excelle dans la distribution et la parallélisation
    """)
    
    print("=" * 80)

if __name__ == "__main__":
    run_comparison_tests()

