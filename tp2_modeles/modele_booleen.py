"""
Modèle Booléen de Recherche d'Information

Le modèle booléen est le plus simple : il retourne les documents qui satisfont
une expression booléenne (AND, OR, NOT) sur les termes de la requête.
"""

from typing import Set, List, Dict
from collections import defaultdict
import re


class ModeleBooleen:
    """Implémentation du modèle booléen de recherche"""
    
    def __init__(self, index_inverse: Dict[str, Set[int]]):
        """
        Initialiser le modèle booléen avec un index inversé
        
        Args:
            index_inverse: Dictionnaire {terme: {doc_ids}}
        """
        self.index = index_inverse
        self.num_docs = max(
            (max(doc_ids) for doc_ids in index_inverse.values() if doc_ids),
            default=0
        )
    
    def get_posting_list(self, term: str) -> Set[int]:
        """Récupérer la liste de postings pour un terme"""
        return self.index.get(term, set())
    
    def search_and(self, terms: List[str]) -> Set[int]:
        """Recherche AND : documents contenant TOUS les termes"""
        if not terms:
            return set()
        
        result = self.get_posting_list(terms[0])
        for term in terms[1:]:
            result = result.intersection(self.get_posting_list(term))
        
        return result
    
    def search_or(self, terms: List[str]) -> Set[int]:
        """Recherche OR : documents contenant AU MOINS UN terme"""
        if not terms:
            return set()
        
        result = self.get_posting_list(terms[0])
        for term in terms[1:]:
            result = result.union(self.get_posting_list(term))
        
        return result
    
    def search_not(self, term: str) -> Set[int]:
        """Recherche NOT : documents ne contenant PAS le terme"""
        term_docs = self.get_posting_list(term)
        all_docs = set(range(1, self.num_docs + 1))
        return all_docs - term_docs
    
    def search_expression(self, query: str) -> Set[int]:
        """
        Rechercher avec une expression booléenne
        
        Supporte les opérateurs AND, OR, NOT
        Exemple: "intelligence AND (artificielle OR machine)"
        """
        # Normaliser la requête
        query = query.upper().strip()
        
        # Parser l'expression booléenne (version simplifiée)
        # Pour une implémentation complète, utiliser un parser d'expressions
        
        # Détecter les opérateurs
        if ' AND ' in query:
            parts = query.split(' AND ')
            terms = [p.strip().strip('()') for p in parts]
            return self.search_and(terms)
        elif ' OR ' in query:
            parts = query.split(' OR ')
            terms = [p.strip().strip('()') for p in parts]
            return self.search_or(terms)
        elif query.startswith('NOT '):
            term = query[4:].strip()
            return self.search_not(term)
        else:
            # Par défaut, recherche AND
            terms = query.split()
            return self.search_and(terms)
    
    def search(self, query: str, processor) -> Set[int]:
        """
        Rechercher avec une requête textuelle
        
        Args:
            query: Requête textuelle
            processor: CorpusProcessor pour pré-traiter la requête
        
        Returns:
            Ensemble des IDs de documents pertinents
        """
        # Pré-traiter la requête
        query_terms = processor.preprocess_text(query)
        
        if not query_terms:
            return set()
        
        # Recherche AND par défaut
        return self.search_and(query_terms)
    
    def get_results_ranked(self, query: str, processor) -> List[int]:
        """
        Retourner les résultats (non classés pour le modèle booléen)
        
        Le modèle booléen ne fait pas de classement, tous les résultats
        sont équivalents.
        """
        results = self.search(query, processor)
        return sorted(list(results))

