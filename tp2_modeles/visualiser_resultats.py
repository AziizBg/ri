"""
Script pour visualiser les résultats de comparaison des modèles
"""

import json
from typing import Dict, List


def load_evaluations(filename='evaluations_llm.json'):
    """Charger les évaluations"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fichier {filename} non trouvé. Exécutez d'abord tp2_main.py")
        return None


def display_detailed_comparison(evaluations: Dict):
    """Afficher une comparaison détaillée"""
    print("=" * 80)
    print("COMPARAISON DÉTAILLÉE DES MODÈLES")
    print("=" * 80)
    
    for query, eval_data in evaluations.items():
        print(f"\n{'='*80}")
        print(f"REQUÊTE: '{query}'")
        print('='*80)
        
        # Afficher les résultats par modèle
        print("\n📋 RÉSULTATS PAR MODÈLE:")
        print("-" * 80)
        
        results = eval_data.get('evaluations', {})
        for model_name, model_eval in results.items():
            scores = model_eval.get('scores', {})
            mean_score = model_eval.get('score_moyen', 0)
            justification = model_eval.get('justification', '')
            
            print(f"\n{model_name}:")
            print(f"  Score moyen: {mean_score:.2f}/10")
            print(f"  Documents retournés: {len(scores)}")
            if scores:
                print(f"  Scores individuels:")
                for doc_id, score in sorted(scores.items(), key=lambda x: float(x[1]), reverse=True)[:5]:
                    print(f"    Doc {doc_id}: {float(score):.2f}/10")
                if len(scores) > 5:
                    print(f"    ... et {len(scores) - 5} autres")
            if justification:
                print(f"  Justification: {justification[:100]}...")
        
        # Afficher la comparaison
        comparison = eval_data.get('comparaison', {})
        best_model = comparison.get('meilleur_modele', 'N/A')
        justification = comparison.get('justification', '')
        
        print(f"\n🏆 MEILLEUR MODÈLE: {best_model}")
        if justification:
            print(f"   Justification: {justification}")


def display_statistics(evaluations: Dict):
    """Afficher les statistiques globales"""
    print("\n" + "=" * 80)
    print("STATISTIQUES GLOBALES")
    print("=" * 80)
    
    model_stats = {}
    
    for query, eval_data in evaluations.items():
        metrics = eval_data.get('metrics', {})
        best_model = eval_data.get('best_model')
        
        for model_name, model_metrics in metrics.items():
            if model_name not in model_stats:
                model_stats[model_name] = {
                    'total_score': 0,
                    'num_queries': 0,
                    'total_results': 0,
                    'wins': 0,
                    'max_scores': []
                }
            
            model_stats[model_name]['total_score'] += model_metrics.get('mean_score', 0)
            model_stats[model_name]['num_queries'] += 1
            model_stats[model_name]['total_results'] += model_metrics.get('num_results', 0)
            model_stats[model_name]['max_scores'].append(model_metrics.get('max_score', 0))
            
            if best_model == model_name:
                model_stats[model_name]['wins'] += 1
    
    # Afficher le tableau
    print(f"\n{'Modèle':<25} {'Score Moyen':<15} {'Résultats/Q':<15} {'Victoires':<10} {'Score Max Moyen':<15}")
    print("-" * 80)
    
    for model_name, stats in sorted(model_stats.items(), key=lambda x: x[1]['wins'], reverse=True):
        avg_score = stats['total_score'] / max(stats['num_queries'], 1)
        avg_results = stats['total_results'] / max(stats['num_queries'], 1)
        avg_max_score = sum(stats['max_scores']) / max(len(stats['max_scores']), 1)
        
        print(f"{model_name:<25} {avg_score:<15.2f} {avg_results:<15.1f} {stats['wins']:<10} {avg_max_score:<15.2f}")
    
    # Identifier le meilleur modèle global
    best_overall = max(model_stats.items(), key=lambda x: (
        x[1]['wins'],
        x[1]['total_score'] / max(x[1]['num_queries'], 1)
    ))
    
    print(f"\n🏆 MEILLEUR MODÈLE GLOBAL: {best_overall[0]}")
    print(f"   Victoires: {best_overall[1]['wins']}/{len(evaluations)} requêtes")
    print(f"   Score moyen: {best_overall[1]['total_score'] / max(best_overall[1]['num_queries'], 1):.2f}/10")


def display_model_characteristics():
    """Afficher les caractéristiques de chaque modèle"""
    print("\n" + "=" * 80)
    print("CARACTÉRISTIQUES DES MODÈLES")
    print("=" * 80)
    
    characteristics = {
        'Booléen': {
            'Avantages': [
                'Simple et rapide',
                'Résultats exacts (pas de faux positifs)',
                'Support des opérateurs booléens (AND, OR, NOT)'
            ],
            'Inconvénients': [
                'Pas de classement (tous les résultats équivalents)',
                'Peut retourner trop ou trop peu de résultats',
                'Pas de notion de pertinence'
            ],
            'Meilleur pour': 'Recherche exacte, filtrage précis'
        },
        'Vectoriel': {
            'Avantages': [
                'Classement par pertinence',
                'Prend en compte la fréquence des termes (TF-IDF)',
                'Bon compromis précision/rappel'
            ],
            'Inconvénients': [
                'Ne capture pas les relations sémantiques',
                'Sensible à la longueur des documents',
                'Hypothèse d\'indépendance des termes'
            ],
            'Meilleur pour': 'Recherche générale avec classement'
        },
        'Probabiliste (BM25)': {
            'Avantages': [
                'Fondement théorique solide',
                'Normalisation de la longueur des documents',
                'Paramètres ajustables (k1, b)',
                'Très performant en pratique'
            ],
            'Inconvénients': [
                'Nécessite un tuning des paramètres',
                'Complexité de calcul plus élevée'
            ],
            'Meilleur pour': 'Recherche générale, moteurs de recherche modernes'
        },
        'Langue': {
            'Avantages': [
                'Modèle probabiliste élégant',
                'Lissage pour gérer les termes absents',
                'Bonne performance sur corpus spécialisés'
            ],
            'Inconvénients': [
                'Peut retourner trop de résultats',
                'Sensible au paramètre lambda',
                'Coût de calcul élevé'
            ],
            'Meilleur pour': 'Recherche dans domaines spécialisés'
        }
    }
    
    for model_name, chars in characteristics.items():
        print(f"\n{model_name}:")
        print(f"  Avantages:")
        for adv in chars['Avantages']:
            print(f"    • {adv}")
        print(f"  Inconvénients:")
        for disadv in chars['Inconvénients']:
            print(f"    • {disadv}")
        print(f"  Meilleur pour: {chars['Meilleur pour']}")


def main():
    """Fonction principale"""
    evaluations = load_evaluations()
    
    if not evaluations:
        return
    
    # Afficher la comparaison détaillée
    display_detailed_comparison(evaluations)
    
    # Afficher les statistiques
    display_statistics(evaluations)
    
    # Afficher les caractéristiques
    display_model_characteristics()
    
    print("\n" + "=" * 80)
    print("Analyse terminée!")
    print("=" * 80)


if __name__ == "__main__":
    main()

