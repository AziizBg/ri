"""
TP Indexation - Partie 3
Création d'un index Elasticsearch et comparaison avec l'implémentation manuelle

Ce module implémente la troisième partie du TP d'indexation qui consiste à :
1. Créer un index Elasticsearch avec un analyzer personnalisé (français)
2. Indexer des documents dans Elasticsearch
3. Comparer les performances avec l'implémentation manuelle
4. Analyser les fonctionnalités avancées d'Elasticsearch (segments, shards, compression)

Elasticsearch est un moteur de recherche distribué qui gère automatiquement
la compression, la maintenance et la parallélisation, ce qui le rend très
efficace pour les gros corpus.
"""

import os  # Pour les opérations sur les fichiers (non utilisé directement ici)
import time  # Pour mesurer les temps d'exécution
import json  # Pour la sérialisation JSON (non utilisé directement ici)
from elasticsearch import Elasticsearch  # Client Python pour Elasticsearch
from elasticsearch.helpers import bulk  # Pour l'indexation en masse (bulk indexing)
from partie1_corpus_et_index import CorpusProcessor, InvertedIndex  # Import des classes de la partie 1


class ElasticsearchIndexer:
    """
    Classe pour gérer l'indexation avec Elasticsearch
    
    Cette classe encapsule toutes les opérations liées à Elasticsearch :
    - Connexion au cluster Elasticsearch
    - Création d'index avec analyzer personnalisé
    - Indexation de documents
    - Recherche dans l'index
    - Analyse des segments et statistiques
    
    Attributes:
        es (Elasticsearch): Client Elasticsearch pour communiquer avec le cluster
        index_name (str): Nom de l'index Elasticsearch utilisé
    """
    
    def __init__(self, host='localhost', port=9200):
        """
        Initialiser le client Elasticsearch
        
        Args:
            host (str): Adresse du serveur Elasticsearch. Par défaut 'localhost'
            port (int): Port du serveur Elasticsearch. Par défaut 9200
        """
        # Créer le client Elasticsearch avec configuration de base
        self.es = Elasticsearch(
            [f'http://{host}:{port}'],  # URL du serveur Elasticsearch
            verify_certs=False,  # Désactiver la vérification des certificats SSL (pour développement)
            ssl_show_warn=False,  # Ne pas afficher les avertissements SSL
            request_timeout=30  # Timeout de 30 secondes pour les requêtes
        )
        # Nom de l'index utilisé pour ce TP
        self.index_name = 'tp_indexation'
        
    def check_connection(self):
        """
        Vérifier la connexion à Elasticsearch
        
        Cette méthode teste si le serveur Elasticsearch est accessible et répond.
        Elle utilise la méthode ping() qui est légère et rapide.
        
        Returns:
            bool: True si la connexion est établie, False sinon
        """
        # Tester la connexion avec ping()
        if self.es.ping():
            print("✓ Connexion à Elasticsearch établie")
            return True
        else:
            print("✗ Impossible de se connecter à Elasticsearch")
            print("  Assurez-vous qu'Elasticsearch est démarré sur localhost:9200")
            return False
    
    def create_index_with_custom_analyzer(self, num_shards=1):
        """
        Créer un index Elasticsearch avec un analyzer personnalisé pour le français
        
        Cette méthode crée un nouvel index avec :
        - Un analyzer personnalisé qui applique les mêmes transformations que notre
          implémentation manuelle (lowercase, stopwords français, stemming français)
        - Un mapping qui définit la structure des documents
        - Configuration du nombre de shards pour la distribution
        
        Args:
            num_shards (int): Nombre de shards pour l'index. Par défaut 1.
                            Plus de shards = meilleure parallélisation mais plus d'overhead
        """
        # Supprimer l'index s'il existe déjà pour repartir de zéro
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
        
        # Définition complète de l'index : settings (configuration) et mappings (structure)
        settings = {
            "settings": {
                "number_of_shards": num_shards,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "custom_french_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "french_stop",
                                "french_stemmer"
                            ]
                        }
                    },
                    "filter": {
                        "french_stop": {
                            "type": "stop",
                            "stopwords": "_french_"
                        },
                        "french_stemmer": {
                            "type": "stemmer",
                            "language": "french"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "custom_french_analyzer",
                        "search_analyzer": "custom_french_analyzer"
                    },
                    "doc_id": {
                        "type": "integer"
                    }
                }
            }
        }
        
        # Créer l'index avec les settings et mappings définis
        # **settings décompresse le dictionnaire en arguments nommés
        self.es.indices.create(index=self.index_name, **settings)
        print(f"✓ Index '{self.index_name}' créé avec {num_shards} shard(s)")
    
    def index_documents(self, documents: list):
        """
        Indexer les documents dans Elasticsearch
        
        Cette méthode indexe une liste de documents en utilisant l'API bulk d'Elasticsearch,
        ce qui est beaucoup plus efficace que d'indexer les documents un par un.
        
        Args:
            documents (list): Liste de dictionnaires contenant les documents à indexer.
                           Chaque document doit avoir :
                           - 'id': Identifiant unique du document
                           - 'text': Contenu textuel du document
        
        Returns:
            tuple: (success, failed) où :
                   - success: Nombre de documents indexés avec succès
                   - failed: Liste des documents qui ont échoué (vide si tout OK)
        """
        # Préparer la liste d'actions pour l'indexation en masse
        actions = []
        for doc in documents:
            # Chaque action définit un document à indexer
            action = {
                "_index": self.index_name,  # Nom de l'index cible
                "_id": doc['id'],  # ID du document (utilise l'ID du corpus)
                "_source": {  # Contenu du document
                    "doc_id": doc['id'],  # ID stocké dans le document
                    "content": doc['text']  # Contenu textuel à indexer
                }
            }
            actions.append(action)
        
        # Exécuter l'indexation en masse avec bulk()
        # chunk_size=100 : traiter 100 documents à la fois pour optimiser les performances
        success, failed = bulk(self.es, actions, chunk_size=100, request_timeout=30)
        print(f"✓ {success} documents indexés, {len(failed)} échecs")
        return success, failed
    
    def analyze_text(self, text: str):
        """
        Analyser un texte avec l'analyzer personnalisé
        
        Cette méthode permet de voir comment Elasticsearch traite un texte donné,
        c'est-à-dire quels tokens sont générés après le pré-traitement.
        Utile pour déboguer et comprendre le processus d'indexation.
        
        Args:
            text (str): Texte à analyser
        
        Returns:
            dict: Résultat de l'analyse contenant la liste des tokens générés
        """
        # Utiliser l'API _analyze d'Elasticsearch
        result = self.es.indices.analyze(
            index=self.index_name,
            analyzer="custom_french_analyzer",  # Utiliser notre analyzer personnalisé
            text=text
        )
        return result
    
    def get_segments_info(self):
        """
        Récupérer les informations sur les segments de l'index
        
        Les segments sont des unités de stockage dans Elasticsearch. Un index peut
        être composé de plusieurs segments qui sont fusionnés (merged) périodiquement.
        
        Returns:
            dict: Informations détaillées sur les segments de l'index
        """
        # Récupérer les informations sur les segments via l'API _segments
        stats = self.es.indices.segments(index=self.index_name)
        return stats
    
    def get_stats(self):
        """
        Récupérer les statistiques complètes de l'index
        
        Cette méthode retourne des statistiques détaillées sur l'index incluant :
        - Nombre de documents
        - Taille sur disque
        - Nombre de segments
        - Et bien d'autres métriques
        
        Returns:
            dict: Statistiques complètes de l'index
        """
        # Récupérer les statistiques via l'API _stats
        stats = self.es.indices.stats(index=self.index_name)
        return stats
    
    def get_index_size(self):
        """
        Obtenir la taille de l'index sur disque
        
        Cette méthode extrait la taille totale de l'index sur disque depuis
        les statistiques. C'est utile pour comparer avec l'implémentation manuelle.
        
        Returns:
            int: Taille de l'index en bytes
        """
        # Récupérer les statistiques
        stats = self.get_stats()
        # Extraire la taille depuis les statistiques
        # Chemin: indices[index_name]['total']['store']['size_in_bytes']
        size_bytes = stats['indices'][self.index_name]['total']['store']['size_in_bytes']
        return size_bytes
    
    def force_merge(self):
        """
        Forcer le merge des segments de l'index
        
        Elasticsearch fusionne automatiquement les segments, mais cette méthode
        force une fusion immédiate pour réduire le nombre de segments à 1.
        Cela peut réduire la taille de l'index et améliorer les performances de recherche.
        
        Note: Cette opération peut être coûteuse en ressources pour les gros index.
        """
        # Forcer le merge pour réduire à 1 segment maximum
        self.es.indices.forcemerge(index=self.index_name, max_num_segments=1)
        print("✓ Force merge effectué")
    
    def search(self, query: str, size=10):
        """
        Rechercher dans l'index Elasticsearch
        
        Cette méthode effectue une recherche full-text dans l'index en utilisant
        une requête de type "match" qui analyse la requête avec le même analyzer
        que celui utilisé pour l'indexation.
        
        Args:
            query (str): Requête de recherche (texte brut)
            size (int): Nombre maximum de résultats à retourner. Par défaut 10
        
        Returns:
            dict: Résultats de la recherche avec les documents correspondants
                 et leurs scores de pertinence
        """
        # Construire le corps de la requête
        query_body = {
            "query": {
                "match": {  # Type de requête : match (recherche full-text)
                    "content": query  # Champ à rechercher
                }
            }
        }
        # Exécuter la recherche
        results = self.es.search(index=self.index_name, body=query_body, size=size)
        return results


def compare_indexation_times(num_shards_list=[1, 2, 4]):
    """
    Comparer les temps d'indexation avec différents nombres de shards
    
    Cette fonction mesure les temps d'indexation pour différents nombres de shards
    afin d'évaluer l'impact de la distribution sur les performances.
    
    Args:
        num_shards_list (list): Liste des nombres de shards à tester. Par défaut [1, 2, 4]
    
    Returns:
        dict: Dictionnaire associant chaque nombre de shards à ses résultats
              (temps d'indexation et taille disque)
    """
    print("\n" + "=" * 60)
    print("COMPARAISON DES TEMPS D'INDEXATION")
    print("=" * 60)
    
    # Créer le corpus
    processor = CorpusProcessor(language='french')
    documents = processor.create_corpus(num_docs=20)
    
    indexer = ElasticsearchIndexer()
    if not indexer.check_connection():
        return
    
    results = {}
    
    for num_shards in num_shards_list:
        print(f"\n--- Test avec {num_shards} shard(s) ---")
        
        # Créer l'index
        indexer.create_index_with_custom_analyzer(num_shards=num_shards)
        
        # Mesurer le temps d'indexation
        start_time = time.time()
        success, failed = indexer.index_documents(documents)
        indexation_time = time.time() - start_time
        
        # Attendre que l'indexation soit terminée
        indexer.es.indices.refresh(index=indexer.index_name)
        
        results[num_shards] = {
            'time': indexation_time,
            'size': indexer.get_index_size()
        }
        
        print(f"Temps d'indexation: {indexation_time:.4f} secondes")
        print(f"Taille disque: {indexer.get_index_size() / 1024:.2f} KB")
    
    # Afficher le résumé
    print("\n--- Résumé ---")
    for num_shards, data in results.items():
        print(f"{num_shards} shard(s): {data['time']:.4f}s, {data['size']/1024:.2f} KB")
    
    return results


def analyze_elasticsearch_features():
    """
    Analyser et visualiser les fonctionnalités d'Elasticsearch
    
    Cette fonction explore les fonctionnalités avancées d'Elasticsearch :
    - Résultat de l'API _analyze (tokens générés)
    - Contenu de l'API _segments (structure des segments)
    - Statistiques de l'API _stats (métriques de l'index)
    - Impact du force merge sur la taille de l'index
    """
    print("\n" + "=" * 60)
    print("ANALYSE DES FONCTIONNALITÉS ELASTICSEARCH")
    print("=" * 60)
    
    indexer = ElasticsearchIndexer()
    if not indexer.check_connection():
        return
    
    # Créer l'index avec 1 shard
    processor = CorpusProcessor(language='french')
    documents = processor.create_corpus(num_docs=20)
    
    indexer.create_index_with_custom_analyzer(num_shards=1)
    indexer.index_documents(documents)
    indexer.es.indices.refresh(index=indexer.index_name)
    
    # 1. Résultat de _analyze
    print("\n1. Résultat de _analyze:")
    sample_text = "L'intelligence artificielle transforme notre société"
    analyze_result = indexer.analyze_text(sample_text)
    print(f"Texte: '{sample_text}'")
    print("Tokens générés:")
    for token in analyze_result['tokens']:
        print(f"  - {token['token']} (position: {token['position']})")
    
    # 2. Contenu de _segments
    print("\n2. Contenu de _segments:")
    segments_info = indexer.get_segments_info()
    print(f"Nombre de segments: {len(segments_info['indices'][indexer.index_name]['shards']['0'])}")
    for shard_id, shard_data in segments_info['indices'][indexer.index_name]['shards'].items():
        for segment in shard_data:
            print(f"  Segment: {segment.get('routing', {}).get('primary', False)}")
            print(f"    Taille: {segment.get('size_in_bytes', 0) / 1024:.2f} KB")
    
    # 3. Statistiques de _stats
    print("\n3. Statistiques de _stats:")
    stats = indexer.get_stats()
    index_stats = stats['indices'][indexer.index_name]
    print(f"Nombre de documents: {index_stats['total']['docs']['count']}")
    print(f"Taille totale: {index_stats['total']['store']['size_in_bytes'] / 1024:.2f} KB")
    print(f"Taille primaire: {index_stats['primaries']['store']['size_in_bytes'] / 1024:.2f} KB")
    
    # 4. Taille avant/après force merge
    print("\n4. Taille avant/après force merge:")
    size_before = indexer.get_index_size()
    print(f"Avant: {size_before / 1024:.2f} KB")
    
    indexer.force_merge()
    indexer.es.indices.refresh(index=indexer.index_name)
    
    size_after = indexer.get_index_size()
    print(f"Après: {size_after / 1024:.2f} KB")
    print(f"Réduction: {(1 - size_after/size_before) * 100:.2f}%")


def compare_with_manual_implementation():
    """
    Comparer Elasticsearch avec l'implémentation manuelle
    
    Cette fonction compare les performances (temps et espace) entre :
    - L'implémentation manuelle de la partie 1
    - Elasticsearch avec analyzer personnalisé
    
    Elle permet d'évaluer les avantages et inconvénients de chaque approche
    et de comprendre comment Elasticsearch gère efficacement la compression,
    la maintenance et la parallélisation.
    """
    print("\n" + "=" * 60)
    print("COMPARAISON ELASTICSEARCH vs IMPLÉMENTATION MANUELLE")
    print("=" * 60)
    
    # Créer le corpus
    processor = CorpusProcessor(language='french')
    documents = processor.create_corpus(num_docs=20)
    
    # === Implémentation manuelle ===
    print("\n--- Implémentation manuelle ---")
    start_time = time.time()
    processed_docs = processor.preprocess_corpus()
    manual_index = InvertedIndex()
    manual_index.build_index(processed_docs)
    manual_time = time.time() - start_time
    manual_size = len(json.dumps({k: list(v) for k, v in manual_index.index.items()}))
    
    print(f"Temps d'indexation: {manual_time:.4f} secondes")
    print(f"Taille mémoire: {manual_size / 1024:.2f} KB")
    
    # === Elasticsearch ===
    print("\n--- Elasticsearch ---")
    indexer = ElasticsearchIndexer()
    if not indexer.check_connection():
        return
    
    indexer.create_index_with_custom_analyzer(num_shards=1)
    start_time = time.time()
    indexer.index_documents(documents)
    indexer.es.indices.refresh(index=indexer.index_name)
    es_time = time.time() - start_time
    es_size = indexer.get_index_size()
    
    print(f"Temps d'indexation: {es_time:.4f} secondes")
    print(f"Taille disque: {es_size / 1024:.2f} KB")
    
    # === Comparaison ===
    print("\n--- Comparaison ---")
    print(f"Temps: Elasticsearch est {manual_time / es_time:.2f}x {'plus rapide' if es_time < manual_time else 'plus lent'}")
    print(f"Taille: Elasticsearch utilise {es_size / manual_size:.2f}x {'plus' if es_size > manual_size else 'moins'} d'espace")
    
    # === Discussion ===
    print("\n" + "=" * 60)
    print("DISCUSSION: GESTION EFFICACE PAR ELASTICSEARCH")
    print("=" * 60)
    print("""
    Compression:
    - Elasticsearch utilise automatiquement la compression LZ4 pour les données
    - Compression des segments lors du merge
    - Compression des données translog
    
    Maintenance:
    - Gestion automatique des segments (merge, refresh)
    - Optimisation automatique des index
    - Gestion des versions de documents (optimistic concurrency)
    - Support natif pour les mises à jour et suppressions
    
    Parallélisation:
    - Distribution automatique sur plusieurs shards
    - Traitement parallèle des requêtes
    - Réplication pour la disponibilité
    - Load balancing automatique
    
    Avantages d'Elasticsearch:
    1. Scalabilité horizontale (ajout de nœuds)
    2. Recherche distribuée et parallèle
    3. Gestion automatique de la fragmentation
    4. Optimisations avancées (caching, compression)
    5. Support de requêtes complexes (booléennes, vectorielles, etc.)
    6. Monitoring et métriques intégrés
    
    Inconvénients:
    1. Overhead pour petits corpus
    2. Complexité de configuration
    3. Consommation mémoire importante
    4. Nécessite une infrastructure dédiée
    """)


def main():
    """
    Fonction principale pour la Partie 3 du TP Indexation
    
    Cette fonction orchestre l'exécution de la troisième partie qui comprend :
    - La comparaison des temps d'indexation avec différents nombres de shards
    - L'analyse des fonctionnalités Elasticsearch (segments, stats, merge)
    - La comparaison avec l'implémentation manuelle
    - L'analyse des compromis et avantages d'Elasticsearch
    
    Note: Nécessite qu'Elasticsearch soit démarré sur localhost:9200
    """
    print("=" * 60)
    print("TP INDEXATION - PARTIE 3")
    print("=" * 60)
    
    # Note: Elasticsearch doit être démarré avant d'exécuter cette partie
    print("\n⚠️  ATTENTION: Assurez-vous qu'Elasticsearch est démarré")
    print("   Commande: docker run -d -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0")
    print("   Ou installez Elasticsearch localement\n")
    
    # Vérifier la connexion
    indexer = ElasticsearchIndexer()
    if not indexer.check_connection():
        print("\n⚠️  Elasticsearch n'est pas disponible. Certaines fonctionnalités seront ignorées.")
        print("   Vous pouvez quand même examiner le code pour comprendre l'implémentation.")
        return
    
    # 1. Comparer les temps d'indexation avec différents nombres de shards
    compare_indexation_times(num_shards_list=[1, 2, 4])
    
    # 2. Analyser les fonctionnalités Elasticsearch
    analyze_elasticsearch_features()
    
    # 3. Comparer avec l'implémentation manuelle
    compare_with_manual_implementation()
    
    print("\n" + "=" * 60)
    print("Partie 3 terminée avec succès!")
    print("=" * 60)


if __name__ == "__main__":
    main()

