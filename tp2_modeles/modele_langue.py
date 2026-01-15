"""
Modèle de Langue de Recherche d'Information

Le modèle de langue estime la probabilité qu'un document ait généré la requête,
en utilisant des modèles de langage unigrammes ou bigrammes.
"""

import math
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import numpy as np


class ModeleLangue:
    """Implémentation du modèle de langue pour la recherche"""
    
    def __init__(self, index_inverse: Dict[str, Set[int]], documents: List[Dict],
                 lambda_param: float = 0.5):
        """
        Initialiser le modèle de langue
        
        Args:
            index_inverse: Index inversé {terme: {doc_ids}}
            documents: Liste des documents pré-traités avec leurs tokens
            lambda_param: Paramètre de lissage (mélange document/collection) (défaut: 0.5)
        """
        self.index = index_inverse
        self.documents = documents
        self.num_docs = len(documents)
        self.lambda_param = lambda_param
        
        # Calculer les fréquences dans les documents
        self.tf = defaultdict(lambda: defaultdict(int))  # tf[doc_id][term] = count
        self.doc_lengths = {}  # Longueur de chaque document
        self.collection_tf = defaultdict(int)  # Fréquence totale dans la collection
        self.collection_length = 0  # Longueur totale de la collection
        
        for doc in documents:
            doc_id = doc['id']
            tokens = doc['tokens']
            self.doc_lengths[doc_id] = len(tokens)
            
            # Compter les occurrences
            for token in tokens:
                self.tf[doc_id][token] += 1
                self.collection_tf[token] += 1
                self.collection_length += 1
        
        # Probabilité de chaque terme dans la collection
        self.collection_prob = {}
        for term, count in self.collection_tf.items():
            self.collection_prob[term] = count / max(self.collection_length, 1)
    
    def _compute_term_probability(self, doc_id: int, term: str) -> float:
        """
        Calculer P(term|document) avec lissage de Jelinek-Mercer
        
        P(term|d) = λ * P(term|d) + (1-λ) * P(term|collection)
        """
        # Probabilité dans le document
        doc_length = self.doc_lengths[doc_id]
        if doc_length == 0:
            doc_prob = 0
        else:
            doc_prob = self.tf[doc_id][term] / doc_length
        
        # Probabilité dans la collection
        collection_prob = self.collection_prob.get(term, 1 / max(self.collection_length, 1))
        
        # Lissage
        prob = self.lambda_param * doc_prob + (1 - self.lambda_param) * collection_prob
        
        return prob
    
    def search(self, query: str, processor, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Rechercher avec le modèle de langue
        
        Le score est la probabilité que le document ait généré la requête:
        P(query|document) = ∏ P(term|document) pour chaque terme de la requête
        
        Args:
            query: Requête textuelle
            processor: CorpusProcessor pour pré-traiter la requête
            top_k: Nombre de résultats à retourner
        
        Returns:
            Liste de tuples (doc_id, score) triés par score décroissant
        """
        # Pré-traiter la requête
        query_terms = processor.preprocess_text(query)
        
        if not query_terms:
            return []
        
        # Calculer les scores pour chaque document
        doc_scores = {}
        
        for doc in self.documents:
            doc_id = doc['id']
            score = 0.0  # Log-probabilité (somme de logs)
            
            for term in query_terms:
                prob = self._compute_term_probability(doc_id, term)
                if prob > 0:
                    score += math.log10(prob)
                else:
                    # Si probabilité nulle, pénaliser fortement
                    score += math.log10(1e-10)
            
            doc_scores[doc_id] = score
        
        # Trier par score décroissant
        scores = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Retourner les top_k résultats
        return scores[:top_k]
    
    def get_results_ranked(self, query: str, processor, top_k: int = 10) -> List[int]:
        """Retourner les IDs de documents classés par pertinence"""
        results = self.search(query, processor, top_k)
        # Les scores sont des log-probabilités (négatifs), on retourne tous les résultats
        return [doc_id for doc_id, score in results]

