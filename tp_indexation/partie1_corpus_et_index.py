"""
TP Indexation - Partie 1
Création d'un corpus, pré-traitement et construction de l'index inversé

Ce module implémente la première partie du TP d'indexation qui consiste à :
1. Créer un corpus de documents textes
2. Pré-traiter les documents (normalisation, tokenisation, suppression des stopwords, stemming)
3. Construire un index inversé permettant de retrouver rapidement les documents contenant un terme
4. Sauvegarder et charger l'index
5. Effectuer des recherches dans l'index

L'index inversé est une structure de données fondamentale en recherche d'information qui
associe chaque terme (mot) à la liste des documents qui le contiennent.
"""

import os  # Pour les opérations sur les fichiers et dossiers
import re  # Pour les expressions régulières (suppression de la ponctuation)
import json  # Pour la sérialisation/désérialisation de l'index en JSON
from collections import defaultdict  # Pour créer des dictionnaires avec valeurs par défaut
from typing import Dict, List, Set  # Pour le typage statique
import nltk  # Bibliothèque de traitement du langage naturel
from nltk.corpus import stopwords  # Liste des mots vides (stopwords) à ignorer
from nltk.tokenize import word_tokenize  # Tokenisation des textes
from nltk.stem import SnowballStemmer  # Réduction des mots à leur racine (stemming)

# Télécharger les ressources NLTK nécessaires si elles ne sont pas déjà présentes
# Ces ressources sont nécessaires pour la tokenisation et le traitement du texte
try:
    # Vérifier si le tokenizer punkt est disponible (utilisé pour la tokenisation)
    nltk.data.find('tokenizers/punkt')
except LookupError:
    # Si non disponible, le télécharger automatiquement
    nltk.download('punkt')

try:
    # Vérifier si punkt_tab est disponible (version améliorée du tokenizer)
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        # Tenter de télécharger punkt_tab
        nltk.download('punkt_tab')
    except:
        # Si punkt_tab n'est pas disponible, on utilisera une tokenisation simple par espaces
        pass

try:
    # Vérifier si les stopwords sont disponibles
    nltk.data.find('corpora/stopwords')
except LookupError:
    # Si non disponibles, les télécharger automatiquement
    nltk.download('stopwords')

class CorpusProcessor:
    """
    Classe pour gérer le corpus et le pré-traitement des documents
    
    Cette classe encapsule toutes les opérations liées au traitement du corpus :
    - Création du corpus à partir de documents texte
    - Pré-traitement des documents (normalisation, tokenisation, stemming)
    - Gestion des ressources NLTK (stopwords, stemmer)
    
    Attributes:
        language (str): Langue utilisée pour le traitement (par défaut 'french')
        stemmer (SnowballStemmer): Objet pour réduire les mots à leur racine
        stop_words (set): Ensemble des mots vides à ignorer lors du traitement
        documents (list): Liste des documents bruts avec leurs métadonnées
        processed_documents (list): Liste des documents pré-traités avec leurs tokens
    """
    
    def __init__(self, language='french'):
        """
        Initialiser le processeur de corpus
        
        Args:
            language (str): Langue du corpus ('french' ou 'english'). Détermine le stemmer
                          et les stopwords à utiliser. Par défaut 'french'.
        """
        self.language = language
        
        # Initialiser le stemmer pour réduire les mots à leur racine
        # Exemple: "intelligence", "intelligent", "intelligemment" -> "intellig"
        self.stemmer = SnowballStemmer(language)
        
        try:
            # Charger les stopwords (mots vides) pour la langue spécifiée
            # Les stopwords sont des mots très fréquents mais peu informatifs
            # (ex: "le", "la", "de", "et", "ou", etc.)
            self.stop_words = set(stopwords.words(language))
        except:
            # Si le français n'est pas disponible, utiliser l'anglais comme fallback
            # Cela permet au code de fonctionner même si les ressources françaises ne sont pas installées
            self.stop_words = set(stopwords.words('english'))
        
        # Liste pour stocker les documents bruts avec leurs métadonnées
        # Format: [{'id': int, 'filename': str, 'text': str}, ...]
        self.documents = []
        
        # Liste pour stocker les documents pré-traités avec leurs tokens
        # Format: [{'id': int, 'tokens': List[str]}, ...]
        self.processed_documents = []
        
    def create_corpus(self, num_docs=20):
        """
        Créer un corpus de documents textes et les sauvegarder dans des fichiers
        
        Cette méthode génère un corpus de documents d'exemple sur différents sujets
        liés à l'informatique et les sauvegarde dans le dossier 'corpus/'.
        
        Args:
            num_docs (int): Nombre de documents à créer. Par défaut 20.
                           Si num_docs > 20, seuls les 20 premiers documents seront créés.
        
        Returns:
            list: Liste des documents créés avec leurs métadonnées.
                  Chaque document est un dictionnaire contenant:
                  - 'id': Identifiant unique du document (commence à 1)
                  - 'filename': Chemin du fichier où le document est sauvegardé
                  - 'text': Contenu textuel du document
        """
        # Documents d'exemple sur différents sujets liés à l'informatique
        # Ces documents servent de corpus de test pour le TP
        sample_documents = [
            "L'intelligence artificielle transforme notre façon de travailler et de vivre.",
            "Les réseaux de neurones profonds permettent de résoudre des problèmes complexes.",
            "Le machine learning utilise des algorithmes pour apprendre à partir de données.",
            "La recherche d'information est un domaine important de l'informatique.",
            "Les moteurs de recherche indexent des millions de pages web quotidiennement.",
            "L'indexation inversée permet de retrouver rapidement les documents pertinents.",
            "Le traitement du langage naturel analyse et comprend le texte humain.",
            "Les algorithmes de compression réduisent la taille des données stockées.",
            "La parallélisation accélère le traitement de grandes quantités d'informations.",
            "Elasticsearch est un moteur de recherche distribué et scalable.",
            "Les bases de données relationnelles stockent les données de manière structurée.",
            "Le cloud computing permet d'accéder aux ressources informatiques à distance.",
            "La cybersécurité protège les systèmes contre les menaces numériques.",
            "Les blockchains garantissent la transparence et la sécurité des transactions.",
            "L'informatique quantique promet de révolutionner le calcul informatique.",
            "Les systèmes distribués répartissent le traitement sur plusieurs machines.",
            "Le big data analyse de vastes ensembles de données pour extraire des insights.",
            "Les APIs permettent la communication entre différents systèmes logiciels.",
            "Le développement agile favorise l'itération rapide et la collaboration.",
            "Les tests automatisés assurent la qualité du code logiciel."
        ]
        
        # Créer le dossier 'corpus' s'il n'existe pas déjà
        # exist_ok=True évite une erreur si le dossier existe déjà
        os.makedirs('corpus', exist_ok=True)
        
        # Créer les fichiers de documents un par un
        # enumerate(sample_documents[:num_docs], 1) permet d'obtenir l'index (commençant à 1)
        # et le texte du document simultanément
        for i, doc_text in enumerate(sample_documents[:num_docs], 1):
            # Générer le nom de fichier avec formatage sur 2 chiffres (doc_01.txt, doc_02.txt, etc.)
            filename = f"corpus/doc_{i:02d}.txt"
            
            # Écrire le contenu du document dans le fichier avec encodage UTF-8
            # pour supporter les caractères accentués français
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(doc_text)
            
            # Ajouter les métadonnées du document à la liste
            self.documents.append({
                'id': i,  # Identifiant unique du document
                'filename': filename,  # Chemin du fichier
                'text': doc_text  # Contenu textuel brut
            })
        
        # Afficher un message de confirmation
        print(f"✓ Corpus créé: {num_docs} documents dans le dossier 'corpus/'")
        return self.documents
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Pré-traiter un texte pour l'indexation
        
        Cette méthode applique une série de transformations au texte pour le préparer
        à l'indexation :
        1. Normalisation (minuscules)
        2. Suppression de la ponctuation
        3. Tokenisation (découpage en mots)
        4. Filtrage des stopwords et tokens trop courts
        5. Stemming (réduction à la racine)
        
        Args:
            text (str): Texte brut à pré-traiter
        
        Returns:
            List[str]: Liste des tokens pré-traités (mots normalisés et réduits à leur racine)
        
        Example:
            >>> processor = CorpusProcessor()
            >>> tokens = processor.preprocess_text("L'intelligence artificielle")
            >>> # Résultat: ['intellig', 'artificiel']
        """
        # Étape 1: Convertir tout le texte en minuscules
        # Cela permet de traiter "Intelligence" et "intelligence" comme le même mot
        text = text.lower()
        
        # Étape 2: Supprimer la ponctuation et les caractères spéciaux
        # r'[^\w\s]' signifie: tout caractère qui n'est pas un mot (\w) ou un espace (\s)
        # Les caractères supprimés sont remplacés par un espace pour éviter la fusion de mots
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Étape 3: Tokenisation - découper le texte en mots individuels
        # Utiliser le tokenizer NLTK si disponible (plus précis que split())
        try:
            # word_tokenize utilise des règles linguistiques pour mieux découper le texte
            # (gère les apostrophes, les contractions, etc.)
            tokens = word_tokenize(text, language='french' if self.language == 'french' else 'english')
        except LookupError:
            # Fallback: si le tokenizer NLTK n'est pas disponible, utiliser split()
            # C'est moins précis mais fonctionne toujours
            tokens = text.split()
        
        # Étape 4: Filtrer les tokens
        # - Supprimer les stopwords (mots vides peu informatifs)
        # - Supprimer les tokens trop courts (longueur <= 2 caractères)
        #   Ces tokens sont souvent des erreurs de tokenisation ou peu informatifs
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        # Étape 5: Stemming - réduire chaque mot à sa racine
        # Exemple: "intelligence", "intelligent", "intelligemment" -> "intellig"
        # Cela permet de regrouper les variantes d'un même mot
        tokens = [self.stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def preprocess_corpus(self):
        """
        Pré-traiter tous les documents du corpus
        
        Cette méthode applique le pré-traitement (normalisation, tokenisation, stemming)
        à tous les documents du corpus et stocke les résultats dans processed_documents.
        
        Returns:
            list: Liste des documents pré-traités. Chaque document contient:
                  - 'id': Identifiant du document
                  - 'tokens': Liste des tokens pré-traités extraits du document
        """
        # Réinitialiser la liste des documents pré-traités
        self.processed_documents = []
        
        # Parcourir tous les documents du corpus
        for doc in self.documents:
            # Appliquer le pré-traitement au texte du document
            processed_tokens = self.preprocess_text(doc['text'])
            
            # Stocker le résultat avec l'identifiant du document
            self.processed_documents.append({
                'id': doc['id'],  # Conserver l'identifiant original
                'tokens': processed_tokens  # Tokens pré-traités
            })
        
        # Afficher un message de confirmation avec le nombre de documents traités
        print(f"✓ Pré-traitement terminé pour {len(self.processed_documents)} documents")
        return self.processed_documents


class InvertedIndex:
    """
    Classe pour construire et gérer l'index inversé
    
    L'index inversé est une structure de données fondamentale en recherche d'information.
    Au lieu de stocker pour chaque document la liste de ses termes (index direct),
    on stocke pour chaque terme la liste des documents qui le contiennent (index inversé).
    
    Structure de l'index:
        index[terme] = {doc_id1, doc_id2, doc_id3, ...}
    
    Cette structure permet de retrouver rapidement tous les documents contenant un terme donné.
    
    Attributes:
        index (Dict[str, Set[int]]): Dictionnaire associant chaque terme à l'ensemble
                                      des identifiants de documents qui le contiennent
        doc_freq (Dict[str, int]): Dictionnaire associant chaque terme au nombre de
                                   documents qui le contiennent (document frequency)
    """
    
    def __init__(self):
        """
        Initialiser un index inversé vide
        
        Utilise defaultdict(set) pour que chaque nouvelle clé soit automatiquement
        associée à un ensemble vide, ce qui simplifie l'ajout de documents.
        """
        # Index inversé: terme -> ensemble de document IDs
        # defaultdict(set) permet d'ajouter directement des éléments sans vérifier
        # si la clé existe déjà
        self.index: Dict[str, Set[int]] = defaultdict(set)
        
        # Document frequency: terme -> nombre de documents contenant ce terme
        # Utile pour calculer des scores de pertinence (ex: TF-IDF)
        self.doc_freq: Dict[str, int] = {}
        
    def build_index(self, processed_documents: List[Dict]):
        """
        Construire l'index inversé à partir des documents pré-traités
        
        Cette méthode parcourt tous les documents pré-traités et construit l'index inversé
        en associant chaque terme unique à l'ensemble des documents qui le contiennent.
        
        Args:
            processed_documents (List[Dict]): Liste des documents pré-traités.
                                            Chaque document doit contenir:
                                            - 'id': Identifiant du document
                                            - 'tokens': Liste des tokens pré-traités
        
        Returns:
            Dict[str, Set[int]]: L'index inversé construit
        
        Note:
            On utilise uniquement les termes uniques par document (set) pour éviter
            de compter plusieurs fois le même document pour un même terme.
        """
        # Réinitialiser l'index et les fréquences
        self.index.clear()
        self.doc_freq.clear()
        
        # Parcourir tous les documents pré-traités
        for doc in processed_documents:
            doc_id = doc['id']  # Identifiant du document
            tokens = doc['tokens']  # Liste des tokens du document
            
            # Convertir la liste de tokens en ensemble pour obtenir les termes uniques
            # Cela évite de traiter plusieurs fois le même terme dans un document
            unique_tokens = set(tokens)
            
            # Pour chaque terme unique dans le document
            for token in unique_tokens:
                # Ajouter l'identifiant du document à la liste de postings du terme
                # Si le terme n'existe pas encore, defaultdict crée automatiquement un set vide
                self.index[token].add(doc_id)
                
                # Incrémenter la document frequency (nombre de documents contenant ce terme)
                # get(token, 0) retourne 0 si le terme n'existe pas encore
                self.doc_freq[token] = self.doc_freq.get(token, 0) + 1
        
        # Afficher un message de confirmation avec le nombre de termes indexés
        print(f"✓ Index inversé construit: {len(self.index)} termes uniques")
        return self.index
    
    def get_posting_list(self, term: str) -> Set[int]:
        """
        Récupérer la liste de postings (numéros de documents) pour un terme
        
        La liste de postings contient tous les identifiants de documents qui contiennent
        le terme spécifié.
        
        Args:
            term (str): Terme pour lequel récupérer la liste de postings
        
        Returns:
            Set[int]: Ensemble des identifiants de documents contenant le terme.
                     Retourne un ensemble vide si le terme n'est pas dans l'index.
        """
        # get(term, set()) retourne l'ensemble de documents pour le terme,
        # ou un ensemble vide si le terme n'existe pas dans l'index
        return self.index.get(term, set())
    
    def search(self, query: str, processor: CorpusProcessor) -> Set[int]:
        """
        Rechercher les documents contenant les termes de la requête
        
        Cette méthode implémente une recherche booléenne AND : elle retourne uniquement
        les documents qui contiennent TOUS les termes de la requête.
        
        Args:
            query (str): Requête de recherche (texte brut)
            processor (CorpusProcessor): Processeur de corpus pour pré-traiter la requête
        
        Returns:
            Set[int]: Ensemble des identifiants de documents correspondant à la requête.
                     Retourne un ensemble vide si aucun document ne correspond ou si
                     la requête est vide après pré-traitement.
        
        Example:
            >>> index.search("intelligence artificielle", processor)
            # Retourne les documents contenant à la fois "intelligence" ET "artificielle"
        """
        # Pré-traiter la requête de la même manière que les documents
        # Cela garantit que les termes de la requête correspondent aux termes de l'index
        query_tokens = processor.preprocess_text(query)
        
        # Si la requête ne contient aucun terme après pré-traitement, retourner un ensemble vide
        if not query_tokens:
            return set()
        
        # Recherche booléenne AND : intersection de toutes les listes de postings
        # Commencer avec la liste de postings du premier terme
        result_docs = self.get_posting_list(query_tokens[0])
        
        # Pour chaque terme suivant, faire l'intersection avec les résultats précédents
        # L'intersection ne garde que les documents présents dans toutes les listes
        for token in query_tokens[1:]:
            result_docs = result_docs.intersection(self.get_posting_list(token))
        
        return result_docs
    
    def save_index(self, filename='index_inverse.json'):
        """
        Sauvegarder l'index inversé dans un fichier JSON
        
        Cette méthode sérialise l'index inversé dans un fichier JSON pour permettre
        sa réutilisation ultérieure sans avoir à reconstruire l'index.
        
        Args:
            filename (str): Nom du fichier où sauvegarder l'index. Par défaut 'index_inverse.json'
        
        Note:
            Les sets sont convertis en listes triées car JSON ne supporte pas nativement
            les ensembles. Le tri facilite la lecture et la comparaison des fichiers.
        """
        # Convertir les sets en listes triées pour la sérialisation JSON
        # JSON ne supporte pas nativement les sets, donc on les convertit en listes
        # Le tri facilite la lecture et la comparaison des fichiers
        index_dict = {term: sorted(list(doc_ids)) for term, doc_ids in self.index.items()}
        
        # Écrire l'index dans le fichier JSON avec indentation pour la lisibilité
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(index_dict, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Index inversé sauvegardé dans '{filename}'")
    
    def load_index(self, filename='index_inverse.json'):
        """
        Charger l'index inversé depuis un fichier JSON
        
        Cette méthode désérialise un index inversé sauvegardé précédemment,
        permettant de réutiliser un index sans avoir à le reconstruire.
        
        Args:
            filename (str): Nom du fichier contenant l'index. Par défaut 'index_inverse.json'
        
        Note:
            Les listes du fichier JSON sont reconverties en sets pour maintenir
            la structure de données originale et optimiser les opérations d'intersection.
        """
        # Lire le fichier JSON contenant l'index
        with open(filename, 'r', encoding='utf-8') as f:
            index_dict = json.load(f)
        
        # Convertir les listes du JSON en sets pour restaurer la structure originale
        # Les sets sont plus efficaces pour les opérations d'intersection lors de la recherche
        self.index = {term: set(doc_ids) for term, doc_ids in index_dict.items()}
        
        # Recalculer les document frequencies à partir des listes de postings
        # doc_freq[term] = nombre de documents contenant le terme
        self.doc_freq = {term: len(doc_ids) for term, doc_ids in index_dict.items()}
        
        print(f"✓ Index inversé chargé depuis '{filename}'")
    
    def print_statistics(self):
        """
        Afficher les statistiques de l'index inversé
        
        Cette méthode affiche diverses statistiques utiles pour comprendre
        la structure et les caractéristiques de l'index :
        - Nombre total de termes uniques
        - Taille moyenne des listes de postings
        - Top 10 des termes les plus fréquents
        - Exemples de listes de postings
        """
        print("\n=== Statistiques de l'index inversé ===")
        
        # Afficher le nombre total de termes uniques dans l'index
        print(f"Nombre de termes uniques: {len(self.index)}")
        
        # Calculer et afficher la taille moyenne des listes de postings
        # C'est le nombre moyen de documents par terme
        if len(self.index) > 0:
            avg_posting_size = sum(len(docs) for docs in self.index.values()) / len(self.index)
            print(f"Taille moyenne des listes de postings: {avg_posting_size:.2f}")
        else:
            print("Taille moyenne des listes de postings: 0.00")
        
        # Trier les termes par document frequency (nombre de documents les contenant)
        # reverse=True pour avoir les plus fréquents en premier
        sorted_terms = sorted(self.doc_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Afficher les 10 termes les plus fréquents
        print("\nTop 10 termes les plus fréquents:")
        for term, freq in sorted_terms[:10]:
            print(f"  {term}: {freq} documents")
        
        # Afficher quelques exemples de listes de postings pour illustrer la structure
        print("\nExemples de listes de postings:")
        # Prendre les 5 premiers termes de l'index (ordre arbitraire)
        for i, (term, doc_ids) in enumerate(list(self.index.items())[:5]):
            # Afficher le terme et la liste triée des documents qui le contiennent
            print(f"  '{term}': {sorted(doc_ids)}")


def main():
    """
    Fonction principale pour la Partie 1 du TP Indexation
    
    Cette fonction orchestre l'exécution complète de la première partie :
    1. Création d'un corpus de documents
    2. Pré-traitement des documents
    3. Construction de l'index inversé
    4. Affichage des statistiques
    5. Sauvegarde de l'index
    6. Tests de recherche avec quelques requêtes d'exemple
    """
    print("=" * 60)
    print("TP INDEXATION - PARTIE 1")
    print("=" * 60)
    
    # Étape 1: Créer le corpus de documents
    print("\n1. Création du corpus...")
    # Initialiser le processeur de corpus en français
    processor = CorpusProcessor(language='french')
    # Créer 20 documents d'exemple et les sauvegarder dans le dossier 'corpus/'
    documents = processor.create_corpus(num_docs=20)
    
    # Étape 2: Pré-traiter tous les documents du corpus
    print("\n2. Pré-traitement du corpus...")
    # Appliquer le pré-traitement (normalisation, tokenisation, stemming) à tous les documents
    processed_docs = processor.preprocess_corpus()
    
    # Étape 3: Construire l'index inversé à partir des documents pré-traités
    print("\n3. Construction de l'index inversé...")
    # Initialiser un nouvel index inversé vide
    index = InvertedIndex()
    # Construire l'index en associant chaque terme aux documents qui le contiennent
    index.build_index(processed_docs)
    
    # Étape 4: Afficher les statistiques de l'index
    # (nombre de termes, fréquences, exemples de postings)
    index.print_statistics()
    
    # Étape 5: Sauvegarder l'index dans un fichier JSON pour réutilisation ultérieure
    print("\n4. Sauvegarde de l'index...")
    index.save_index('index_inverse.json')
    
    # Étape 6: Tester la recherche avec quelques requêtes d'exemple
    print("\n5. Test de recherche...")
    # Définir quelques requêtes de test pour valider le fonctionnement de la recherche
    test_queries = [
        "intelligence artificielle",
        "recherche information",
        "machine learning"
    ]
    
    # Exécuter chaque requête et afficher les résultats
    for query in test_queries:
        # Rechercher les documents correspondant à la requête
        results = index.search(query, processor)
        # Afficher la requête et les documents trouvés (triés par ID)
        print(f"\nRequête: '{query}'")
        print(f"Documents trouvés: {sorted(results)}")
    
    # Message de fin d'exécution
    print("\n" + "=" * 60)
    print("Partie 1 terminée avec succès!")
    print("=" * 60)


if __name__ == "__main__":
    main()

