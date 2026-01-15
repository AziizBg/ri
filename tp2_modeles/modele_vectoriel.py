"""
Modèle Vectoriel de Recherche d'Information (TF-IDF)

Le modèle vectoriel représente les documents et requêtes comme des vecteurs
dans un espace vectoriel et calcule la similarité cosinus.
"""

import math
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import numpy as np


class ModeleVectoriel:
    """Implémentation du modèle vectoriel avec TF-IDF"""
    
    def __init__(self, index_inverse: Dict[str, Set[int]], documents: List[Dict]):
        """
        Initialiser le modèle vectoriel
        
        Args:
            index_inverse: Index inversé {terme: {doc_ids}}
            documents: Liste des documents pré-traités avec leurs tokens
        """
        self.index = index_inverse
        self.documents = documents
        self.num_docs = len(documents)
        
        # Construire le vocabulaire
        self.vocabulary = sorted(list(index_inverse.keys()))
        self.term_to_idx = {term: idx for idx, term in enumerate(self.vocabulary)}
        
        # Calculer les fréquences de termes dans les documents
        self.tf = defaultdict(lambda: defaultdict(int))  # tf[doc_id][term] = count
        self.df = defaultdict(int)  # df[term] = nombre de documents contenant le terme
        
        for doc in documents:
            doc_id = doc['id']
            tokens = doc['tokens']
            
            # Compter les occurrences de chaque terme
            for token in tokens:
                if token in self.vocabulary:
                    self.tf[doc_id][token] += 1
                    if self.tf[doc_id][token] == 1:  # Première occurrence dans ce document
                        self.df[token] += 1
        
        # Calculer les vecteurs TF-IDF pour chaque document
        self.doc_vectors = {}
        self._compute_tfidf_vectors()
    
    def _compute_tfidf_vectors(self):
        """Calculer les vecteurs TF-IDF pour tous les documents"""
        for doc in self.documents:
            doc_id = doc['id']
            vector = np.zeros(len(self.vocabulary))
            
            for term in self.vocabulary:
                if term in self.tf[doc_id]:
                    # TF (Term Frequency) - normalisation logarithmique
                    tf_value = 1 + math.log10(self.tf[doc_id][term])
                    
                    # IDF (Inverse Document Frequency)
                    idf_value = math.log10(self.num_docs / max(self.df[term], 1))
                    
                    # TF-IDF
                    tfidf = tf_value * idf_value
                    vector[self.term_to_idx[term]] = tfidf
            
            # Normalisation du vecteur (norme L2)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            self.doc_vectors[doc_id] = vector
    
    def _compute_query_vector(self, query_terms: List[str]) -> np.ndarray:
        """Calculer le vecteur TF-IDF pour une requête"""
        vector = np.zeros(len(self.vocabulary))
        
        # Compter les occurrences dans la requête
        query_tf = defaultdict(int)
        for term in query_terms:
            if term in self.vocabulary:
                query_tf[term] += 1
        
        # Calculer TF-IDF pour la requête
        for term, count in query_tf.items():
            # TF normalisé
            tf_value = 1 + math.log10(count)
            
            # IDF (même que pour les documents)
            idf_value = math.log10(self.num_docs / max(self.df[term], 1))
            
            # TF-IDF
            tfidf = tf_value * idf_value
            vector[self.term_to_idx[term]] = tfidf
        
        # Normalisation
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def search(self, query: str, processor, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Rechercher avec le modèle vectoriel
        
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
        
        # Calculer le vecteur de la requête
        query_vector = self._compute_query_vector(query_terms)
        
        # Calculer la similarité cosinus avec tous les documents
        scores = []
        for doc_id, doc_vector in self.doc_vectors.items():
            # Similarité cosinus = produit scalaire (car vecteurs normalisés)
            similarity = np.dot(query_vector, doc_vector)
            scores.append((doc_id, similarity))
        
        # Trier par score décroissant
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner les top_k résultats
        return scores[:top_k]
    
    def get_results_ranked(self, query: str, processor, top_k: int = 10) -> List[int]:
        """Retourner les IDs de documents classés par pertinence"""
        results = self.search(query, processor, top_k)
        return [doc_id for doc_id, score in results if score > 0]

