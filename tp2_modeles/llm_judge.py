"""
LLM as a Judge - Évaluation comparative des modèles de recherche

Ce module utilise un LLM (Large Language Model) pour évaluer et comparer
les résultats de différents modèles de recherche d'information.
"""

import json
import os
from typing import List, Dict, Tuple
from openai import OpenAI
from anthropic import Anthropic


class LLMJudge:
    """Utilise un LLM pour juger la pertinence des résultats de recherche"""
    
    def __init__(self, provider: str = 'openai', model: str = 'gpt-4o-mini'):
        """
        Initialiser le LLM Judge
        
        Args:
            provider: 'openai' ou 'anthropic'
            model: Nom du modèle à utiliser
        """
        self.provider = provider
        self.model = model
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            # Essayer aussi de lire depuis un fichier .env
            if not api_key:
                try:
                    env_path = os.path.join(os.path.dirname(__file__), '.env')
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as f:
                            for line in f:
                                if line.startswith('OPENAI_API_KEY='):
                                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                    break
                except Exception as e:
                    pass
            if not api_key:
                print("⚠️  OPENAI_API_KEY non défini. Utilisez 'export OPENAI_API_KEY=votre_cle' ou créez un fichier .env")
            self.client = OpenAI(api_key=api_key) if api_key else None
        elif provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            # Essayer aussi de lire depuis un fichier .env
            if not api_key:
                try:
                    env_path = os.path.join(os.path.dirname(__file__), '.env')
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as f:
                            for line in f:
                                if line.startswith('ANTHROPIC_API_KEY='):
                                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                    break
                except Exception as e:
                    pass
            if not api_key:
                print("⚠️  ANTHROPIC_API_KEY non défini. Utilisez 'export ANTHROPIC_API_KEY=votre_cle' ou créez un fichier .env")
            self.client = Anthropic(api_key=api_key) if api_key else None
        else:
            raise ValueError(f"Provider non supporté: {provider}")
    
    def evaluate_query(self, query: str, documents: List[Dict], 
                      results_by_model: Dict[str, List[int]]) -> Dict:
        """
        Évaluer les résultats de différents modèles pour une requête
        
        Args:
            query: Requête de recherche
            documents: Liste de tous les documents avec leur contenu
            results_by_model: Dictionnaire {nom_modele: [doc_ids]}
        
        Returns:
            Dictionnaire avec les évaluations
        """
        if not self.client:
            return self._mock_evaluation(query, results_by_model)
        
        # Préparer le contexte pour le LLM
        context = self._prepare_context(query, documents, results_by_model)
        
        # Appeler le LLM
        prompt = self._create_evaluation_prompt(context)
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un expert en recherche d'information. Tu évalues la pertinence des résultats de recherche."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                evaluation_text = response.choices[0].message.content
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                evaluation_text = response.content[0].text
            
            # Parser la réponse
            evaluation = self._parse_evaluation(evaluation_text, results_by_model)
            return evaluation
            
        except Exception as e:
            print(f"Erreur lors de l'appel au LLM: {e}")
            return self._mock_evaluation(query, results_by_model)
    
    def _prepare_context(self, query: str, documents: List[Dict],
                        results_by_model: Dict[str, List[int]]) -> Dict:
        """Préparer le contexte pour l'évaluation"""
        context = {
            'query': query,
            'documents': {},
            'results': {}
        }
        
        # Ajouter les documents pertinents
        all_doc_ids = set()
        for doc_ids in results_by_model.values():
            all_doc_ids.update(doc_ids)
        
        for doc in documents:
            if doc['id'] in all_doc_ids:
                context['documents'][doc['id']] = doc.get('text', '')
        
        # Ajouter les résultats par modèle
        context['results'] = results_by_model
        
        return context
    
    def _create_evaluation_prompt(self, context: Dict) -> str:
        """Créer le prompt pour l'évaluation"""
        query = context['query']
        documents = context['documents']
        results = context['results']
        
        prompt = f"""Évalue la pertinence des résultats de recherche pour la requête suivante.

REQUÊTE: "{query}"

DOCUMENTS RETRIEVÉS:
"""
        for doc_id, text in documents.items():
            prompt += f"\nDocument {doc_id}: {text}\n"
        
        prompt += "\n\nRÉSULTATS PAR MODÈLE:\n"
        for model_name, doc_ids in results.items():
            prompt += f"\n{model_name}: Documents {sorted(doc_ids)}\n"
        
        prompt += """
ÉVALUATION DEMANDÉE:
1. Pour chaque modèle, évalue la pertinence des documents retournés (0-10 pour chaque document)
2. Compare les modèles et identifie lequel retourne les résultats les plus pertinents
3. Donne une justification pour chaque évaluation

Format de réponse (JSON):
{
  "evaluations": {
    "nom_modele": {
      "scores": {"doc_id": score},
      "score_moyen": float,
      "justification": "texte"
    }
  },
  "comparaison": {
    "meilleur_modele": "nom",
    "justification": "texte"
  }
}
"""
        return prompt
    
    def _parse_evaluation(self, text: str, results_by_model: Dict) -> Dict:
        """Parser la réponse du LLM"""
        try:
            # Essayer d'extraire le JSON
            if '```json' in text:
                json_start = text.find('```json') + 7
                json_end = text.find('```', json_start)
                json_text = text[json_start:json_end].strip()
            elif '```' in text:
                json_start = text.find('```') + 3
                json_end = text.find('```', json_start)
                json_text = text[json_start:json_end].strip()
            else:
                # Chercher le premier { et dernier }
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                json_text = text[json_start:json_end]
            
            evaluation = json.loads(json_text)
            return evaluation
        except:
            # Si le parsing échoue, retourner une évaluation mock
            return self._mock_evaluation("", results_by_model)
    
    def _mock_evaluation(self, query: str, results_by_model: Dict) -> Dict:
        """Évaluation mock quand le LLM n'est pas disponible"""
        evaluations = {}
        for model_name, doc_ids in results_by_model.items():
            scores = {str(doc_id): 7.0 for doc_id in doc_ids}
            evaluations[model_name] = {
                "scores": scores,
                "score_moyen": 7.0,
                "justification": "Évaluation mock (LLM non disponible)"
            }
        
        return {
            "evaluations": evaluations,
            "comparaison": {
                "meilleur_modele": list(results_by_model.keys())[0] if results_by_model else None,
                "justification": "Comparaison mock - configurez une clé API pour une vraie évaluation"
            }
        }
    
    def compare_models(self, query: str, documents: List[Dict],
                      results_by_model: Dict[str, List[int]],
                      scores_by_model: Dict[str, Dict[int, float]] = None) -> Dict:
        """
        Comparer les résultats de différents modèles
        
        Args:
            query: La requête de recherche
            documents: Liste des documents avec leur texte
            results_by_model: Dictionnaire {nom_modele: [doc_ids]}
            scores_by_model: Dictionnaire {nom_modele: {doc_id: score}}
        
        Returns:
            Dictionnaire avec comparaison détaillée
        """
        evaluation = self.evaluate_query(query, documents, results_by_model)
        
        # Comparer les modèles vectoriel et probabiliste si ils retournent les mêmes documents
        vectoriel_results = results_by_model.get('Vectoriel', [])
        probabiliste_results = results_by_model.get('Probabiliste (BM25)', [])
        
        # Vérifier si les résultats sont identiques
        if (vectoriel_results == probabiliste_results and 
            len(vectoriel_results) > 0 and scores_by_model):
            # Comparer l'ordre et les scores
            vectoriel_scores = scores_by_model.get('Vectoriel', {})
            probabiliste_scores = scores_by_model.get('Probabiliste (BM25)', {})
            
            # Comparer les ordres (les listes sont déjà triées par score)
            order_same = vectoriel_results == probabiliste_results
            
            # Comparer les scores
            score_diffs = []
            for doc_id in vectoriel_results:
                vec_score = vectoriel_scores.get(doc_id, 0)
                prob_score = probabiliste_scores.get(doc_id, 0)
                if vec_score > 0 or prob_score > 0:
                    score_diffs.append((doc_id, vec_score, prob_score, abs(vec_score - prob_score)))
            
            # Si les résultats sont identiques, modifier la justification
            if order_same and all(diff < 0.01 for _, _, _, diff in score_diffs):
                # Les modèles sont pratiquement identiques
                meilleur_modele = evaluation.get('comparaison', {}).get('meilleur_modele', '')
                if meilleur_modele in ['Vectoriel', 'Probabiliste (BM25)']:
                    justification = (
                        f"Les modèles Vectoriel et Probabiliste (BM25) retournent exactement "
                        f"les mêmes documents dans le même ordre avec des scores très similaires. "
                        f"Ils sont tous les deux les meilleurs pour cette requête. "
                        f"{evaluation.get('comparaison', {}).get('justification', '')}"
                    )
                    evaluation['comparaison']['meilleur_modele'] = 'Vectoriel et Probabiliste (BM25)'
                    evaluation['comparaison']['justification'] = justification
            elif order_same:
                # Même ordre mais scores différents
                diff_str = ', '.join([f"doc_{d}: {v:.3f} vs {p:.3f}" for d, v, p, _ in score_diffs[:3]])
                justification = (
                    f"Les modèles Vectoriel et Probabiliste (BM25) retournent les mêmes documents "
                    f"dans le même ordre, mais avec des scores légèrement différents: {diff_str}. "
                    f"{evaluation.get('comparaison', {}).get('justification', '')}"
                )
                evaluation['comparaison']['justification'] = justification
        
        # Calculer des métriques supplémentaires
        comparison = {
            'query': query,
            'evaluations': evaluation.get('evaluations', {}),
            'best_model': evaluation.get('comparaison', {}).get('meilleur_modele'),
            'justification': evaluation.get('comparaison', {}).get('justification', ''),
            'metrics': {}
        }
        
        # Métriques par modèle
        for model_name, eval_data in evaluation.get('evaluations', {}).items():
            scores = eval_data.get('scores', {})
            # Convertir les scores en float si nécessaire
            score_values = []
            for score in scores.values():
                try:
                    score_values.append(float(score))
                except (ValueError, TypeError):
                    score_values.append(0.0)
            
            comparison['metrics'][model_name] = {
                'mean_score': eval_data.get('score_moyen', 0),
                'num_results': len(results_by_model.get(model_name, [])),
                'max_score': max(score_values) if score_values else 0,
                'min_score': min(score_values) if score_values else 0
            }
        
        return comparison

