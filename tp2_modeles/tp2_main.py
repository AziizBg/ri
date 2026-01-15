"""
TP2 - Comparaison des Modèles de Recherche d'Information
Utilise LLM as a Judge pour évaluer les différents modèles
"""

import os
import sys
import json
from typing import List, Dict

# Ajouter le chemin du TP1 pour importer les classes
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tp_indexation'))

from partie1_corpus_et_index import CorpusProcessor, InvertedIndex
from modele_booleen import ModeleBooleen
from modele_vectoriel import ModeleVectoriel
from modele_probabiliste import ModeleProbabiliste
from modele_langue import ModeleLangue
from llm_judge import LLMJudge


def create_corpus_tp2(num_docs=50):
    """Créer un corpus pour le TP2 avec plusieurs domaines distincts"""
    # Créer le corpus dans un dossier spécifique pour le TP2
    original_dir = os.getcwd()
    corpus_dir = 'corpus_tp2'
    os.makedirs(corpus_dir, exist_ok=True)
    
    processor = CorpusProcessor(language='french')
    
    # Documents organisés par domaine pour mieux démontrer la pertinence
    documents_by_domain = {
        'informatique_ia': [
            "L'intelligence artificielle transforme notre façon de travailler et de vivre.",
            "Les réseaux de neurones profonds permettent de résoudre des problèmes complexes.",
            "Le machine learning utilise des algorithmes pour apprendre à partir de données.",
            "Le deep learning utilise des réseaux de neurones à plusieurs couches.",
            "Les modèles de langage génèrent du texte de manière autonome.",
            "Les transformers révolutionnent le traitement du langage naturel.",
            "L'apprentissage automatique s'améliore avec plus de données.",
            "La vision par ordinateur permet aux machines de comprendre les images.",
            "Les réseaux de neurones convolutifs excellent en vision par ordinateur.",
            "Les réseaux de neurones récurrents gèrent les séquences temporelles."
        ],
        'recherche_information': [
            "La recherche d'information est un domaine important de l'informatique.",
            "Les moteurs de recherche indexent des millions de pages web quotidiennement.",
            "L'indexation inversée permet de retrouver rapidement les documents pertinents.",
            "Elasticsearch est un moteur de recherche distribué et scalable.",
            "La recherche sémantique comprend le sens des requêtes.",
            "Les métadonnées enrichissent les documents avec des informations supplémentaires.",
            "L'extraction d'information identifie les entités nommées dans les textes.",
            "La similarité sémantique mesure la proximité de sens entre termes.",
            "Les embeddings vectoriels représentent les mots comme des vecteurs.",
            "Les ontologies définissent les relations entre concepts."
        ],
        'systemes_distribues': [
            "Les systèmes distribués répartissent le traitement sur plusieurs machines.",
            "Le cloud computing permet d'accéder aux ressources informatiques à distance.",
            "Les bases de données relationnelles stockent les données de manière structurée.",
            "Le big data analyse de vastes ensembles de données pour extraire des insights.",
            "La parallélisation accélère le traitement de grandes quantités d'informations.",
            "Les APIs permettent la communication entre différents systèmes logiciels.",
            "Les algorithmes de compression réduisent la taille des données stockées.",
            "Les structures de données organisent l'information efficacement.",
            "Les graphes modélisent les relations entre entités.",
            "L'optimisation algorithmique améliore les performances des programmes."
        ],
        'cybersecurite': [
            "La cybersécurité protège les systèmes contre les menaces numériques.",
            "Les blockchains garantissent la transparence et la sécurité des transactions.",
            "Les systèmes experts imitent le raisonnement des spécialistes.",
            "L'informatique quantique promet de révolutionner le calcul informatique.",
            "Les tests automatisés assurent la qualité du code logiciel.",
            "Le développement agile favorise l'itération rapide et la collaboration.",
            "La reconnaissance vocale convertit la parole en texte.",
            "Les chatbots utilisent le traitement du langage naturel pour converser.",
            "Le traitement du langage naturel analyse et comprend le texte humain.",
            "La résolution de coréférence lie les pronoms à leurs référents."
        ],
        'medecine': [
            "La médecine moderne utilise des techniques d'imagerie médicale avancées.",
            "Les vaccins ont permis d'éradiquer de nombreuses maladies infectieuses.",
            "La chirurgie robotique améliore la précision des interventions chirurgicales.",
            "La génétique médicale permet de diagnostiquer des maladies héréditaires.",
            "Les antibiotiques combattent les infections bactériennes.",
            "La radiologie utilise les rayons X pour visualiser les structures internes.",
            "La pharmacologie étudie les effets des médicaments sur l'organisme.",
            "L'épidémiologie analyse la distribution des maladies dans les populations.",
            "La neurologie traite les troubles du système nerveux.",
            "La cardiologie se concentre sur les maladies du cœur et des vaisseaux."
        ],
        'histoire': [
            "La Révolution française a marqué un tournant dans l'histoire européenne.",
            "L'Empire romain a dominé la Méditerranée pendant plusieurs siècles.",
            "La Seconde Guerre mondiale a causé des millions de morts.",
            "La Renaissance a vu un renouveau artistique et scientifique en Europe.",
            "L'Antiquité grecque a posé les bases de la philosophie occidentale.",
            "Le Moyen Âge a été une période de développement culturel et religieux.",
            "La découverte de l'Amérique a changé le cours de l'histoire mondiale.",
            "L'industrialisation a transformé les sociétés au XIXe siècle.",
            "Les croisades ont été des expéditions militaires vers le Moyen-Orient.",
            "La Guerre froide a opposé les États-Unis et l'Union soviétique."
        ],
        'sciences': [
            "La théorie de la relativité d'Einstein a révolutionné la physique.",
            "L'évolution des espèces explique la diversité de la vie sur Terre.",
            "La photosynthèse permet aux plantes de produire de l'énergie.",
            "L'ADN contient l'information génétique de tous les êtres vivants.",
            "Les atomes sont les constituants fondamentaux de la matière.",
            "La gravitation maintient les planètes en orbite autour du soleil.",
            "Les cellules sont les unités de base de tous les organismes vivants.",
            "La thermodynamique étudie les transformations de l'énergie.",
            "La mécanique quantique décrit le comportement des particules subatomiques.",
            "L'écologie examine les interactions entre les organismes et leur environnement."
        ],
        'litterature': [
            "La poésie utilise le langage pour créer des images et des émotions.",
            "Le roman raconte des histoires fictives ou réelles de manière narrative.",
            "Le théâtre met en scène des dialogues et des actions devant un public.",
            "La littérature classique française comprend des auteurs comme Molière et Racine.",
            "Les fables utilisent des animaux pour transmettre des leçons morales.",
            "La science-fiction explore des mondes imaginaires et des technologies futures.",
            "Le réalisme décrit la société de manière objective et détaillée.",
            "Le romantisme privilégie l'émotion et l'expression personnelle.",
            "La nouvelle est un récit court et concentré.",
            "L'autobiographie raconte la vie de l'auteur à la première personne."
        ]
    }
    
    # Créer la liste de tous les documents avec leurs domaines
    all_documents = []
    doc_id = 1
    
    # Distribuer les documents de manière équilibrée entre les domaines
    domains = list(documents_by_domain.keys())
    docs_per_domain = num_docs // len(domains)
    remaining = num_docs % len(domains)
    
    for domain_idx, domain in enumerate(domains):
        domain_docs = documents_by_domain[domain]
        # Prendre plus de documents pour les premiers domaines si nécessaire
        num_docs_for_domain = docs_per_domain + (1 if domain_idx < remaining else 0)
        
        for i in range(num_docs_for_domain):
            if doc_id > num_docs:
                break
            doc_text = domain_docs[i % len(domain_docs)]
            all_documents.append({
                'id': doc_id,
                'text': doc_text,
                'domain': domain,
                'filename': f'{corpus_dir}/doc_{doc_id:02d}.txt'
            })
            doc_id += 1
            if doc_id > num_docs:
                break
    
    # Sauvegarder les documents
    for doc in all_documents:
        with open(doc['filename'], 'w', encoding='utf-8') as f:
            f.write(doc['text'])
    
    processor.documents = all_documents
    print(f"✓ Corpus créé: {len(all_documents)} documents dans '{corpus_dir}/'")
    print(f"  Domaines: {', '.join(set(d['domain'] for d in all_documents))}")
    
    return processor, all_documents


def build_all_models(processor: CorpusProcessor, documents: List[Dict]):
    """Construire tous les modèles de recherche"""
    # Pré-traiter le corpus
    processed_docs = processor.preprocess_corpus()
    
    # Construire l'index inversé
    index = InvertedIndex()
    index.build_index(processed_docs)
    
    # Créer les modèles
    models = {
        'Booléen': ModeleBooleen(index.index),
        'Vectoriel': ModeleVectoriel(index.index, processed_docs),
        'Probabiliste (BM25)': ModeleProbabiliste(index.index, processed_docs),
        'Langue': ModeleLangue(index.index, processed_docs)
    }
    
    return models, processed_docs


def test_queries(models: Dict, processor: CorpusProcessor, 
                processed_docs: List[Dict], queries: List[str]):
    """Tester les modèles avec différentes requêtes"""
    results = {}
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"REQUÊTE: '{query}'")
        print('='*60)
        
        query_results = {}
        query_scores = {}  # Stocker les scores pour chaque modèle
        
        # Tester chaque modèle
        for model_name, model in models.items():
            try:
                if model_name == 'Booléen':
                    doc_ids = model.search(query, processor)
                    ranked_results = sorted(list(doc_ids))
                    scores = {doc_id: 1.0 for doc_id in ranked_results}  # Score binaire
                else:
                    # Récupérer les résultats avec scores
                    scored_results = model.search(query, processor, top_k=10)
                    # Le modèle de langue retourne des log-probabilités (négatives)
                    # Il faut donc ne pas filtrer par score > 0 pour ce modèle
                    if model_name == 'Langue':
                        ranked_results = [doc_id for doc_id, score in scored_results]
                        scores = {doc_id: score for doc_id, score in scored_results}
                    else:
                        ranked_results = [doc_id for doc_id, score in scored_results if score > 0]
                        scores = {doc_id: score for doc_id, score in scored_results if score > 0}
                
                query_results[model_name] = ranked_results
                query_scores[model_name] = scores
                
                print(f"\n{model_name}:")
                print(f"  Documents trouvés: {ranked_results[:10]}")
                if len(ranked_results) > 10:
                    print(f"  ... et {len(ranked_results) - 10} autres")
                # Afficher les scores pour les modèles non-booléens
                if model_name != 'Booléen' and ranked_results:
                    print(f"  Scores: {[f'{scores.get(doc_id, 0):.3f}' for doc_id in ranked_results[:5]]}")
                
            except Exception as e:
                print(f"  Erreur avec {model_name}: {e}")
                query_results[model_name] = []
                query_scores[model_name] = {}
        
        results[query] = {
            'results': query_results,
            'scores': query_scores
        }
    
    return results


def evaluate_with_llm(results: Dict, documents: List[Dict], 
                      processed_docs: List[Dict], processor: CorpusProcessor):
    """Évaluer les résultats avec LLM as a Judge"""
    print("\n" + "="*60)
    print("ÉVALUATION AVEC LLM AS A JUDGE")
    print("="*60)
    
    # Créer le judge
    judge = LLMJudge(provider='openai', model='gpt-4o-mini')
    
    # Préparer les documents avec texte original
    docs_with_text = []
    for doc in documents:
        docs_with_text.append({
            'id': doc['id'],
            'text': doc['text']
        })
    
    all_evaluations = {}
    
    for query, query_data in results.items():
        print(f"\n--- Évaluation pour: '{query}' ---")
        
        # Extraire les résultats et scores
        query_results = query_data['results']
        query_scores = query_data['scores']
        
        # Comparer les modèles
        comparison = judge.compare_models(
            query=query,
            documents=docs_with_text,
            results_by_model=query_results,
            scores_by_model=query_scores
        )
        
        all_evaluations[query] = comparison
        
        # Afficher les résultats
        print(f"\nMeilleur modèle: {comparison['best_model']}")
        print(f"Justification: {comparison['justification']}")
        
        print("\nScores par modèle:")
        for model_name, metrics in comparison['metrics'].items():
            print(f"  {model_name}:")
            mean_score = metrics.get('mean_score', 0)
            if mean_score is not None:
                print(f"    Score moyen: {mean_score:.2f}")
            else:
                print(f"    Score moyen: N/A")
            print(f"    Nombre de résultats: {metrics.get('num_results', 0)}")
            max_score = metrics.get('max_score', 0)
            if isinstance(max_score, (int, float)):
                print(f"    Score max: {max_score:.2f}")
            else:
                print(f"    Score max: {max_score}")
    
    return all_evaluations


def generate_comparison_report(evaluations: Dict):
    """Générer un rapport de comparaison"""
    print("\n" + "="*60)
    print("RAPPORT DE COMPARAISON")
    print("="*60)
    
    # Statistiques globales
    model_stats = {}
    
    for query, eval_data in evaluations.items():
        for model_name, metrics in eval_data['metrics'].items():
            if model_name not in model_stats:
                model_stats[model_name] = {
                    'total_score': 0,
                    'num_queries': 0,
                    'total_results': 0,
                    'wins': 0
                }
            
            mean_score = metrics.get('mean_score', 0)
            if mean_score is not None:
                model_stats[model_name]['total_score'] += mean_score
            model_stats[model_name]['num_queries'] += 1
            model_stats[model_name]['total_results'] += metrics.get('num_results', 0)
            
            if eval_data['best_model'] == model_name:
                model_stats[model_name]['wins'] += 1
    
    print("\n📊 STATISTIQUES GLOBALES")
    print("-"*60)
    print(f"{'Modèle':<25} {'Score Moyen':<15} {'Résultats/Q':<15} {'Victoires':<10}")
    print("-"*60)
    
    for model_name, stats in model_stats.items():
        avg_score = stats['total_score'] / max(stats['num_queries'], 1)
        avg_results = stats['total_results'] / max(stats['num_queries'], 1)
        print(f"{model_name:<25} {avg_score:<15.2f} {avg_results:<15.1f} {stats['wins']:<10}")
    
    # Sauvegarder les résultats
    with open('evaluations_llm.json', 'w', encoding='utf-8') as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Évaluations sauvegardées dans 'evaluations_llm.json'")


def main():
    """Fonction principale du TP2"""
    print("="*60)
    print("TP2 - COMPARAISON DES MODÈLES DE RECHERCHE")
    print("="*60)
    
    # 1. Créer le corpus
    print("\n1. Création du corpus...")
    processor, documents = create_corpus_tp2(num_docs=50)
    
    # 2. Construire tous les modèles
    print("\n2. Construction des modèles...")
    models, processed_docs = build_all_models(processor, documents)
    print(f"✓ {len(models)} modèles construits")
    
    # 3. Définir les requêtes de test
    test_queries_list = [
        "intelligence artificielle",
        "recherche d'information",
        "machine learning et deep learning",
        "systèmes distribués",
        "cybersécurité et blockchain"
    ]
    
    # 4. Tester les requêtes
    print("\n3. Test des requêtes...")
    results = test_queries(models, processor, processed_docs, test_queries_list)
    
    # 5. Évaluation avec LLM
    print("\n4. Évaluation avec LLM as a Judge...")
    evaluations = evaluate_with_llm(results, documents, processed_docs, processor)
    
    # 6. Générer le rapport
    print("\n5. Génération du rapport...")
    generate_comparison_report(evaluations)
    
    print("\n" + "="*60)
    print("TP2 terminé avec succès!")
    print("="*60)


if __name__ == "__main__":
    main()

