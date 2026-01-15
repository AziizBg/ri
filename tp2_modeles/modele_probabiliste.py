"""
Modèle Probabiliste de Recherche d'Information (BM25)

Le modèle probabiliste BM25 (Best Matching 25) est une amélioration du modèle
probabiliste classique qui prend en compte la longueur des documents.
"""

import math
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import numpy as np


class ModeleProbabiliste:
    """Implémentation du modèle probabiliste BM25"""
    
    def __init__(self, index_inverse: Dict[str, Set[int]], documents: List[Dict],
                 k1: float = 1.5, b: float = 0.75):
        """
        Initialiser le modèle probabiliste BM25
        
        Args:
            index_inverse: Index inversé {terme: {doc_ids}}
            documents: Liste des documents pré-traités avec leurs tokens
            k1: Paramètre de saturation de la fréquence de terme (défaut: 1.5)
            b: Paramètre de normalisation de la longueur (défaut: 0.75)
        """
        self.index = index_inverse
        self.documents = documents
        self.num_docs = len(documents)
        self.k1 = k1
        self.b = b
        
        # Calculer les fréquences et longueurs
        self.tf = defaultdict(lambda: defaultdict(int))  # tf[doc_id][term] = count
        self.df = defaultdict(int)  # df[term] = nombre de documents contenant le terme
        self.doc_lengths = {}  # Longueur de chaque document (nombre de termes)
        
        for doc in documents:
            doc_id = doc['id']
            tokens = doc['tokens']
            self.doc_lengths[doc_id] = len(tokens)
            
            # Compter les occurrences
            for token in tokens:
                self.tf[doc_id][token] += 1
                if self.tf[doc_id][token] == 1:
                    self.df[token] += 1
        
        # Longueur moyenne des documents
        if self.doc_lengths:
            self.avg_doc_length = sum(self.doc_lengths.values()) / len(self.doc_lengths)
        else:
            self.avg_doc_length = 0
    
    def _compute_idf(self, term: str) -> float:
        """Calculer l'IDF pour un terme"""
        if self.df[term] == 0:
            return 0
        return math.log10((self.num_docs - self.df[term] + 0.5) / (self.df[term] + 0.5))
    
    def _compute_bm25_score(self, doc_id: int, term: str) -> float:
        """Calculer le score BM25 pour un terme dans un document"""
        if term not in self.tf[doc_id]:
            return 0
        
        # Fréquence du terme dans le document
        tf = self.tf[doc_id][term]
        
        # Longueur du document
        doc_length = self.doc_lengths[doc_id]
        
        # IDF
        idf = self._compute_idf(term)
        
        # Score BM25
        # BM25(t, d) = IDF(t) * (tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * |d|/avgdl))
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / max(self.avg_doc_length, 1)))
        
        score = idf * (numerator / denominator)
        return score
    
    def search(self, query: str, processor, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Rechercher avec le modèle probabiliste BM25
        
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
        
        # Calculer les scores BM25 pour chaque document
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.index:
                # Pour chaque document contenant le terme
                for doc_id in self.index[term]:
                    score = self._compute_bm25_score(doc_id, term)
                    doc_scores[doc_id] += score
        
        # Trier par score décroissant
        scores = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Retourner les top_k résultats
        return scores[:top_k]
    
    def get_results_ranked(self, query: str, processor, top_k: int = 10) -> List[int]:
        """Retourner les IDs de documents classés par pertinence"""
        results = self.search(query, processor, top_k)
        return [doc_id for doc_id, score in results if score > 0]

