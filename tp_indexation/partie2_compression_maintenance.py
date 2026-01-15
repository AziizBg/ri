"""
TP Indexation - Partie 2
Implémentation des modules: compression, maintenance, parallélisation

Ce module implémente la deuxième partie du TP d'indexation qui traite de :
1. Compression de l'index inversé (gap encoding, variable-byte encoding)
2. Maintenance de l'index (ajout, suppression, mise à jour de documents)
3. Parallélisation de la construction d'index pour améliorer les performances
4. Mesure et comparaison des performances (temps, espace mémoire)

La compression permet de réduire l'espace mémoire/disque occupé par l'index,
au prix d'un léger overhead lors de la décompression lors des recherches.
La parallélisation permet d'accélérer la construction de l'index pour les gros corpus.
"""

import json  # Pour la sérialisation JSON (non utilisé directement ici mais importé pour compatibilité)
import time  # Pour mesurer les temps d'exécution
import pickle  # Pour la sérialisation Python (compression)
import gzip  # Pour la compression gzip des fichiers
from collections import defaultdict  # Pour les dictionnaires avec valeurs par défaut
from typing import Dict, List, Set  # Pour le typage statique
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor  # Pour la parallélisation
import multiprocessing as mp  # Pour obtenir le nombre de CPU disponibles
from partie1_corpus_et_index import CorpusProcessor, InvertedIndex  # Import des classes de la partie 1


class CompressedIndex:
    """
    Classe pour la compression de l'index inversé
    
    Cette classe implémente différentes techniques de compression pour réduire
    la taille mémoire de l'index inversé. Les listes de postings (doc_ids) sont
    souvent triées et contiennent des valeurs consécutives ou proches, ce qui
    permet une compression efficace.
    
    Attributes:
        index (Dict[str, List[int]]): Index compressé où les listes de postings
                                      sont encodées sous forme de gaps ou autres
                                      représentations compressées
    """
    
    def __init__(self):
        """
        Initialiser un index compressé vide
        """
        # L'index compressé stocke les listes de postings sous forme compressée
        # (gaps au lieu de valeurs absolues)
        self.index: Dict[str, List[int]] = {}
        
    def compress_gap_encoding(self, doc_ids: List[int]) -> List[int]:
        """
        Compression par encodage des gaps (différences)
        
        Le gap encoding consiste à remplacer chaque valeur par la différence
        avec la valeur précédente. Comme les listes de postings sont souvent
        triées et contiennent des valeurs proches, les gaps sont généralement
        plus petits que les valeurs absolues, permettant une compression.
        
        Exemple:
            [1, 3, 5, 7, 10] -> [1, 2, 2, 2, 3]
            (1, 1+2=3, 3+2=5, 5+2=7, 7+3=10)
        
        Args:
            doc_ids (List[int]): Liste des identifiants de documents (non triée)
        
        Returns:
            List[int]: Liste compressée avec gaps. Le premier élément est la
                      valeur absolue, les suivants sont les différences.
        """
        # Si la liste est vide, retourner une liste vide
        if not doc_ids:
            return []
        
        # Trier les IDs pour que les gaps soient positifs et minimaux
        sorted_ids = sorted(doc_ids)
        
        # Le premier élément est la valeur absolue
        gaps = [sorted_ids[0]]
        
        # Les éléments suivants sont les différences (gaps) avec l'élément précédent
        for i in range(1, len(sorted_ids)):
            gaps.append(sorted_ids[i] - sorted_ids[i-1])
        
        return gaps
    
    def decompress_gap_encoding(self, gaps: List[int]) -> List[int]:
        """
        Décompression des gaps pour restaurer la liste originale d'IDs
        
        Cette méthode inverse le processus de compression : elle reconstruit
        la liste originale d'identifiants de documents à partir des gaps.
        
        Args:
            gaps (List[int]): Liste compressée avec gaps
        
        Returns:
            List[int]: Liste originale des identifiants de documents
        """
        # Si la liste est vide, retourner une liste vide
        if not gaps:
            return []
        
        # Le premier élément est la valeur absolue
        doc_ids = [gaps[0]]
        
        # Reconstruire les valeurs en additionnant les gaps successifs
        for i in range(1, len(gaps)):
            doc_ids.append(doc_ids[i-1] + gaps[i])
        
        return doc_ids
    
    def compress_variable_byte(self, number: int) -> bytes:
        """
        Compression variable-byte encoding
        
        Le variable-byte encoding encode un entier sur un nombre variable d'octets.
        Chaque octet utilise 7 bits pour les données et 1 bit pour indiquer si
        l'octet suivant fait partie du même nombre (bit de continuation).
        
        Principe:
        - Si number < 128: encodé sur 1 octet (bit de continuation = 0)
        - Sinon: encodé sur plusieurs octets, chaque octet sauf le dernier
                 a son bit de continuation = 1
        
        Args:
            number (int): Nombre entier à compresser
        
        Returns:
            bytes: Représentation compressée du nombre en variable-byte
        """
        result = []
        
        # Encoder le nombre par chunks de 7 bits
        while number >= 128:
            # Prendre les 7 bits de poids faible et mettre le bit de continuation à 1
            # (| 128) met le bit le plus significatif à 1
            result.append((number % 128) | 128)
            # Décaler de 7 bits vers la droite
            number //= 128
        
        # Le dernier octet n'a pas de bit de continuation (bit = 0)
        result.append(number % 128)
        
        return bytes(result)
    
    def decompress_variable_byte(self, byte_data: bytes) -> int:
        """
        Décompression variable-byte encoding
        
        Reconstruit le nombre original à partir de sa représentation
        variable-byte.
        
        Args:
            byte_data (bytes): Données compressées en variable-byte
        
        Returns:
            int: Nombre original décompressé
        """
        number = 0
        shift = 0  # Décalage en bits pour reconstruire le nombre
        
        # Parcourir chaque octet
        for byte_val in byte_data:
            # Extraire les 7 bits de données (masquer le bit de continuation)
            # et les décaler selon la position
            number += (byte_val & 127) << shift
            shift += 7  # Chaque octet représente 7 bits
            
            # Si le bit de continuation est 0, c'est le dernier octet
            if byte_val < 128:
                break
        
        return number
    
    def compress_index(self, index: Dict[str, Set[int]], method='gap'):
        """
        Compresser l'index inversé complet
        
        Applique la compression à toutes les listes de postings de l'index.
        
        Args:
            index (Dict[str, Set[int]]): Index inversé non compressé
            method (str): Méthode de compression à utiliser. 'gap' pour gap encoding,
                         autre valeur pour pas de compression (stockage direct)
        
        Returns:
            Dict[str, List[int]]: Index compressé
        """
        # Réinitialiser l'index compressé
        self.index.clear()
        
        # Parcourir tous les termes de l'index
        for term, doc_ids in index.items():
            # Trier les IDs pour que la compression soit efficace
            sorted_ids = sorted(list(doc_ids))
            
            # Appliquer la méthode de compression choisie
            if method == 'gap':
                # Utiliser le gap encoding
                self.index[term] = self.compress_gap_encoding(sorted_ids)
            else:
                # Pas de compression, stocker directement
                self.index[term] = sorted_ids
        
        return self.index
    
    def get_size_memory(self) -> int:
        """
        Estimer la taille mémoire de l'index compressé
        
        Utilise pickle pour sérialiser l'index et mesurer sa taille.
        C'est une approximation de la taille mémoire réelle.
        
        Returns:
            int: Taille estimée en bytes
        """
        # Sérialiser l'index avec pickle et mesurer la taille
        return len(pickle.dumps(self.index))
    
    def save_compressed(self, filename='index_compressed.pkl.gz'):
        """
        Sauvegarder l'index compressé dans un fichier
        
        L'index est sérialisé avec pickle puis compressé avec gzip pour
        réduire encore plus la taille sur disque.
        
        Args:
            filename (str): Nom du fichier de sortie. Par défaut 'index_compressed.pkl.gz'
        """
        # Ouvrir le fichier en mode binaire avec compression gzip
        with gzip.open(filename, 'wb') as f:
            # Sérialiser l'index avec pickle et l'écrire dans le fichier compressé
            pickle.dump(self.index, f)
        
        print(f"✓ Index compressé sauvegardé dans '{filename}'")
    
    def load_compressed(self, filename='index_compressed.pkl.gz'):
        """
        Charger l'index compressé depuis un fichier
        
        Args:
            filename (str): Nom du fichier à charger. Par défaut 'index_compressed.pkl.gz'
        """
        # Ouvrir le fichier compressé en mode lecture binaire
        with gzip.open(filename, 'rb') as f:
            # Désérialiser l'index depuis le fichier
            self.index = pickle.load(f)
        
        print(f"✓ Index compressé chargé depuis '{filename}'")


class IndexMaintenance:
    """
    Classe pour la maintenance de l'index (ajout, suppression, mise à jour)
    
    Cette classe permet de modifier dynamiquement l'index inversé sans avoir
    à le reconstruire entièrement. Elle gère les opérations CRUD (Create, Read,
    Update, Delete) sur les documents de l'index.
    
    Attributes:
        index (InvertedIndex): L'index inversé à maintenir
        pending_updates (list): Liste des mises à jour en attente (non utilisée actuellement)
    """
    
    def __init__(self, index: InvertedIndex):
        """
        Initialiser le gestionnaire de maintenance
        
        Args:
            index (InvertedIndex): L'index inversé à maintenir
        """
        self.index = index
        # Liste pour stocker les mises à jour en attente (pour batch updates)
        self.pending_updates = []
        
    def add_document(self, doc_id: int, tokens: List[str]):
        """
        Ajouter un nouveau document à l'index
        
        Cette méthode met à jour l'index pour inclure un nouveau document.
        Pour chaque terme unique du document, elle ajoute l'ID du document
        à la liste de postings du terme et met à jour la document frequency.
        
        Args:
            doc_id (int): Identifiant unique du nouveau document
            tokens (List[str]): Liste des tokens pré-traités du document
        """
        # Utiliser uniquement les termes uniques pour éviter les doublons
        unique_tokens = set(tokens)
        
        # Pour chaque terme unique du document
        for token in unique_tokens:
            # Ajouter l'ID du document à la liste de postings du terme
            # defaultdict crée automatiquement un set vide si le terme n'existe pas
            self.index.index[token].add(doc_id)
            
            # Incrémenter la document frequency (nombre de documents contenant ce terme)
            self.index.doc_freq[token] = self.index.doc_freq.get(token, 0) + 1
    
    def remove_document(self, doc_id: int):
        """
        Supprimer un document de l'index
        
        Cette méthode retire toutes les références à un document de l'index.
        Elle parcourt tous les termes et supprime l'ID du document de leurs
        listes de postings. Si un terme n'a plus aucun document, il est supprimé.
        
        Args:
            doc_id (int): Identifiant du document à supprimer
        
        Note:
            Complexité: O(n) où n est le nombre total de termes dans l'index.
            C'est coûteux car il faut parcourir tous les termes.
        """
        # Liste des termes à supprimer (ceux qui n'ont plus aucun document)
        terms_to_remove = []
        
        # Parcourir tous les termes de l'index
        for term, doc_ids in self.index.index.items():
            # Si le document est présent dans la liste de postings de ce terme
            if doc_id in doc_ids:
                # Retirer l'ID du document de la liste de postings
                doc_ids.remove(doc_id)
                
                # Décrémenter la document frequency
                self.index.doc_freq[term] -= 1
                
                # Si le terme n'a plus aucun document, le marquer pour suppression
                if self.index.doc_freq[term] == 0:
                    terms_to_remove.append(term)
        
        # Supprimer les termes qui n'ont plus de documents
        for term in terms_to_remove:
            del self.index.index[term]
            del self.index.doc_freq[term]
    
    def update_document(self, doc_id: int, new_tokens: List[str]):
        """
        Mettre à jour un document dans l'index
        
        Cette méthode remplace le contenu d'un document existant. Elle fonctionne
        en supprimant d'abord l'ancienne version puis en ajoutant la nouvelle.
        
        Args:
            doc_id (int): Identifiant du document à mettre à jour
            new_tokens (List[str]): Nouveaux tokens pré-traités du document
        """
        # Supprimer l'ancienne version du document
        self.remove_document(doc_id)
        # Ajouter la nouvelle version
        self.add_document(doc_id, new_tokens)
    
    def merge_indexes(self, other_index: Dict[str, Set[int]]):
        """
        Fusionner deux index
        
        Cette méthode fusionne un autre index dans l'index actuel. Les listes
        de postings sont fusionnées (union) et les document frequencies sont
        recalculées.
        
        Args:
            other_index (Dict[str, Set[int]]): L'autre index à fusionner
        """
        # Parcourir tous les termes de l'autre index
        for term, doc_ids in other_index.items():
            # Fusionner les listes de postings (union des sets)
            self.index.index[term].update(doc_ids)
            
            # Recalculer la document frequency après la fusion
            self.index.doc_freq[term] = len(self.index.index[term])


def process_document_batch(args):
    """
    Fonction pour traiter un batch de documents (pour parallélisation)
    
    Cette fonction est exécutée dans un processus séparé pour traiter un batch
    de documents en parallèle. Elle applique le pré-traitement à tous les documents
    du batch.
    
    Args:
        args (tuple): Tuple contenant:
                     - doc_batch (List[Dict]): Liste des documents à traiter
                     - language (str): Langue pour le pré-traitement
    
    Returns:
        List[Dict]: Liste des documents pré-traités avec leurs tokens
    """
    # Déballer les arguments
    doc_batch, language = args
    
    # Créer un nouveau processeur pour ce processus (nécessaire car chaque
    # processus a sa propre mémoire)
    processor = CorpusProcessor(language=language)
    results = []
    
    # Pré-traiter chaque document du batch
    for doc in doc_batch:
        tokens = processor.preprocess_text(doc['text'])
        results.append({
            'id': doc['id'],
            'tokens': tokens
        })
    
    return results


class ParallelIndexBuilder:
    """
    Classe pour construire l'index en parallèle
    
    Cette classe utilise le multiprocessing pour paralléliser le pré-traitement
    des documents, ce qui peut accélérer significativement la construction de l'index
    pour les gros corpus.
    
    Attributes:
        num_workers (int): Nombre de processus workers à utiliser pour la parallélisation
    """
    
    def __init__(self, num_workers=None):
        """
        Initialiser le constructeur d'index parallèle
        
        Args:
            num_workers (int, optional): Nombre de workers. Si None, utilise
                                       le nombre de CPU disponibles
        """
        # Utiliser le nombre de CPU disponibles si non spécifié
        self.num_workers = num_workers or mp.cpu_count()
    
    def build_index_parallel(self, documents: List[Dict], language='french'):
        """
        Construire l'index en parallèle
        
        Cette méthode divise les documents en batches et les traite en parallèle
        sur plusieurs processus, puis fusionne les résultats pour construire l'index final.
        
        Args:
            documents (List[Dict]): Liste des documents bruts à indexer
            language (str): Langue pour le pré-traitement. Par défaut 'french'
        
        Returns:
            tuple: (index, processed_docs) où:
                   - index: L'index inversé construit
                   - processed_docs: Liste de tous les documents pré-traités
        """
        # Diviser les documents en batches pour la distribution sur les workers
        # Chaque worker traitera environ len(documents) / num_workers documents
        batch_size = max(1, len(documents) // self.num_workers)
        batches = []
        
        # Créer les batches en découpant la liste de documents
        for i in range(0, len(documents), batch_size):
            batches.append(documents[i:i+batch_size])
        
        # Traiter les batches en parallèle avec ProcessPoolExecutor
        # ProcessPoolExecutor utilise des processus séparés (pas des threads)
        # ce qui permet de contourner le GIL de Python pour un vrai parallélisme
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Mapper la fonction process_document_batch sur chaque batch
            # Chaque batch est traité dans un processus séparé
            results = list(executor.map(
                process_document_batch,
                [(batch, language) for batch in batches]
            ))
        
        # Fusionner les résultats de tous les batches
        processed_docs = []
        for batch_results in results:
            processed_docs.extend(batch_results)
        
        # Construire l'index final à partir de tous les documents pré-traités
        # Cette étape est séquentielle car elle nécessite l'accès à l'index global
        index = InvertedIndex()
        index.build_index(processed_docs)
        
        return index, processed_docs


def measure_performance():
    """
    Mesurer les performances avant/après parallélisation et compression
    
    Cette fonction effectue une série de mesures de performance pour comparer :
    1. Les temps d'indexation séquentielle vs parallèle
    2. Les tailles mémoire avant et après compression
    3. Les temps d'opérations de maintenance (ajout, suppression)
    
    Les résultats permettent d'évaluer les compromis espace/temps des différentes
    approches et de déterminer quand utiliser la parallélisation ou la compression.
    """
    print("=" * 60)
    print("MESURE DES PERFORMANCES")
    print("=" * 60)
    
    # Créer le corpus de test (20 documents)
    processor = CorpusProcessor(language='french')
    documents = processor.create_corpus(num_docs=20)
    
    # === MESURE 1: Temps d'indexation séquentiel vs parallèle ===
    print("\n1. Temps d'indexation:")
    
    # Mesure séquentielle : traitement document par document dans l'ordre
    start_time = time.time()
    processed_docs = processor.preprocess_corpus()
    index_seq = InvertedIndex()
    index_seq.build_index(processed_docs)
    time_seq = time.time() - start_time
    print(f"  Séquentiel: {time_seq:.4f} secondes")
    
    # Mesure parallèle : traitement distribué sur plusieurs processus
    parallel_builder = ParallelIndexBuilder(num_workers=4)
    start_time = time.time()
    index_par, _ = parallel_builder.build_index_parallel(documents)
    time_par = time.time() - start_time
    print(f"  Parallèle (4 workers): {time_par:.4f} secondes")
    # Calculer le facteur d'accélération
    print(f"  Accélération: {time_seq / time_par:.2f}x")
    
    # === MESURE 2: Taille mémoire avant/après compression ===
    print("\n2. Taille mémoire:")
    
    # Mesurer la taille de l'index non compressé
    # Utiliser pickle pour sérialiser et mesurer la taille
    size_uncompressed = len(pickle.dumps(index_seq.index))
    print(f"  Non compressé: {size_uncompressed:,} bytes ({size_uncompressed/1024:.2f} KB)")
    
    # Compresser l'index avec gap encoding
    compressed_index = CompressedIndex()
    compressed_index.compress_index(index_seq.index, method='gap')
    size_compressed = compressed_index.get_size_memory()
    print(f"  Compressé (gap): {size_compressed:,} bytes ({size_compressed/1024:.2f} KB)")
    # Calculer le ratio de compression
    print(f"  Ratio de compression: {size_uncompressed / size_compressed:.2f}x")
    
    # Sauvegarder l'index compressé pour démonstration
    compressed_index.save_compressed('index_compressed.pkl.gz')
    
    # === MESURE 3: Test de maintenance ===
    print("\n3. Test de maintenance:")
    # Créer un gestionnaire de maintenance pour l'index séquentiel
    maintenance = IndexMaintenance(index_seq)
    
    # Test d'ajout d'un nouveau document
    new_doc = {
        'id': 21,
        'text': "Les nouvelles technologies transforment notre société."
    }
    # Pré-traiter le nouveau document
    new_tokens = processor.preprocess_text(new_doc['text'])
    # Mesurer le temps d'ajout
    start_time = time.time()
    maintenance.add_document(21, new_tokens)
    time_add = time.time() - start_time
    print(f"  Ajout d'un document: {time_add:.6f} secondes")
    
    # Test de suppression du document ajouté
    start_time = time.time()
    maintenance.remove_document(21)
    time_remove = time.time() - start_time
    print(f"  Suppression d'un document: {time_remove:.6f} secondes")
    
    # === DISCUSSION DES COMPROMIS ===
    print("\n" + "=" * 60)
    print("DISCUSSION DES COMPROMIS ESPACE/TEMPS")
    print("=" * 60)
    print("""
    Compromis Compression:
    - Avantage: Réduction significative de l'espace mémoire/disque
    - Inconvénient: Temps de décompression nécessaire lors de la recherche
    - Méthode gap encoding: Simple et efficace pour les listes de postings triées
    
    Compromis Parallélisation:
    - Avantage: Accélération du traitement pour de gros volumes
    - Inconvénient: Overhead de communication entre processus
    - Efficace pour: Corpus volumineux (>1000 documents)
    - Moins efficace pour: Petits corpus (overhead > gain)
    
    Compromis Maintenance:
    - Ajout: O(1) par terme, très rapide
    - Suppression: O(n) où n est le nombre de termes, nécessite parcours complet
    - Mise à jour: Coût de suppression + ajout
    """)


def main():
    """
    Fonction principale pour la Partie 2 du TP Indexation
    
    Cette fonction orchestre l'exécution de la deuxième partie qui comprend :
    - La mesure des performances de compression
    - La mesure des performances de parallélisation
    - Les tests de maintenance de l'index
    - L'analyse des compromis espace/temps
    """
    print("=" * 60)
    print("TP INDEXATION - PARTIE 2")
    print("=" * 60)
    
    # Exécuter toutes les mesures de performance
    measure_performance()
    
    # Message de fin d'exécution
    print("\n" + "=" * 60)
    print("Partie 2 terminée avec succès!")
    print("=" * 60)


if __name__ == "__main__":
    main()

