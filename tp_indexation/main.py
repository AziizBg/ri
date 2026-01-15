"""
Script principal pour exécuter les différentes parties du TP Indexation

Ce module sert de point d'entrée principal pour l'exécution des différentes parties
du TP d'indexation. Il permet de lancer individuellement ou collectivement les
trois parties du projet :
- Partie 1 : Création du corpus, pré-traitement et construction de l'index inversé
- Partie 2 : Compression, maintenance et parallélisation de l'index
- Partie 3 : Intégration avec Elasticsearch et comparaison des performances

Usage:
    python main.py 1    # Exécuter uniquement la partie 1
    python main.py 2    # Exécuter uniquement la partie 2
    python main.py 3    # Exécuter uniquement la partie 3
    python main.py 0    # Exécuter toutes les parties
"""

import sys
import argparse

def run_partie1():
    """
    Exécuter la Partie 1 du TP Indexation
    
    Cette fonction lance l'exécution de la première partie qui comprend :
    - La création d'un corpus de documents textes
    - Le pré-traitement des documents (tokenisation, normalisation, stemming)
    - La construction d'un index inversé
    - La sauvegarde de l'index et des statistiques
    """
    print("\n" + "="*60)
    print("EXÉCUTION DE LA PARTIE 1")
    print("="*60 + "\n")
    # Import dynamique pour éviter les imports circulaires
    from partie1_corpus_et_index import main
    main()

def run_partie2():
    """
    Exécuter la Partie 2 du TP Indexation
    
    Cette fonction lance l'exécution de la deuxième partie qui comprend :
    - L'implémentation de techniques de compression (gap encoding, variable-byte)
    - La maintenance de l'index (ajout, suppression, mise à jour de documents)
    - La parallélisation de la construction d'index
    - La mesure et comparaison des performances
    """
    print("\n" + "="*60)
    print("EXÉCUTION DE LA PARTIE 2")
    print("="*60 + "\n")
    # Import dynamique pour éviter les imports circulaires
    from partie2_compression_maintenance import main
    main()

def run_partie3():
    """
    Exécuter la Partie 3 du TP Indexation
    
    Cette fonction lance l'exécution de la troisième partie qui comprend :
    - La création d'un index Elasticsearch avec analyzer personnalisé
    - L'indexation des documents dans Elasticsearch
    - La comparaison des performances avec l'implémentation manuelle
    - L'analyse des fonctionnalités avancées d'Elasticsearch (segments, shards, etc.)
    
    Note: Nécessite qu'Elasticsearch soit démarré sur localhost:9200
    """
    print("\n" + "="*60)
    print("EXÉCUTION DE LA PARTIE 3")
    print("="*60 + "\n")
    # Import dynamique pour éviter les imports circulaires
    from partie3_elasticsearch import main
    main()

def main():
    """
    Fonction principale du script
    
    Configure et exécute le parser d'arguments en ligne de commande pour permettre
    à l'utilisateur de choisir quelle(s) partie(s) du TP exécuter.
    
    Arguments acceptés:
        - 1 : Exécuter uniquement la partie 1
        - 2 : Exécuter uniquement la partie 2
        - 3 : Exécuter uniquement la partie 3
        - 0 : Exécuter toutes les parties séquentiellement
    """
    # Création du parser d'arguments avec description
    parser = argparse.ArgumentParser(description='TP Indexation - Système de Recherche d\'Information')
    
    # Ajout de l'argument 'partie' avec validation des valeurs acceptées
    parser.add_argument('partie', type=int, choices=[1, 2, 3, 0], 
                       help='Numéro de la partie à exécuter (0 pour toutes)')
    
    # Parsing des arguments de la ligne de commande
    args = parser.parse_args()
    
    # Exécution conditionnelle selon le choix de l'utilisateur
    if args.partie == 0:
        # Exécuter toutes les parties dans l'ordre
        run_partie1()
        run_partie2()
        run_partie3()
    elif args.partie == 1:
        run_partie1()
    elif args.partie == 2:
        run_partie2()
    elif args.partie == 3:
        run_partie3()

# Point d'entrée du script : exécution uniquement si le fichier est lancé directement
if __name__ == "__main__":
    main()

