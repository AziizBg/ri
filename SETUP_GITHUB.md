# Instructions pour créer le repository GitHub

## 1. Créer le repository sur GitHub

1. Aller sur [GitHub](https://github.com)
2. Cliquer sur "New repository"
3. Nommer le repository (ex: `sri-tp-indexation-modeles`)
4. **Ne pas** initialiser avec README, .gitignore ou LICENSE (déjà présents)
5. Cliquer sur "Create repository"

## 2. Connecter le repository local à GitHub

```bash
cd /Users/azizbenghorbel/Downloads/ri

# Ajouter le remote (remplacer USERNAME et REPO_NAME)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Ou avec SSH
git remote add origin git@github.com:USERNAME/REPO_NAME.git
```

## 3. Vérifier les fichiers à committer

```bash
# Voir les fichiers qui seront ajoutés
git status

# Vérifier que les fichiers sensibles sont ignorés
git status --ignored
```

## 4. Faire le premier commit

```bash
# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Vérifier ce qui sera commité
git status

# Faire le commit
git commit -m "Initial commit: TP Indexation et TP2 Modèles de Recherche

- TP Indexation: Index inversé, compression, maintenance, parallélisation, Elasticsearch
- TP2 Modèles: Booléen, Vectoriel, BM25, Langue avec LLM as a Judge
- Rapports complets inclus
- Documentation complète"
```

## 5. Pousser vers GitHub

```bash
# Renommer la branche en 'main' (si nécessaire)
git branch -M main

# Pousser vers GitHub
git push -u origin main
```

## 6. Vérifier sur GitHub

- Vérifier que tous les fichiers sont présents
- Vérifier que les fichiers sensibles (venv/, *.json, corpus/) ne sont pas présents
- Vérifier que le README.md s'affiche correctement

## Fichiers qui NE DOIVENT PAS être sur GitHub

Les fichiers suivants sont automatiquement ignorés grâce à `.gitignore` :
- `venv/` (environnements virtuels)
- `__pycache__/` (cache Python)
- `*.json` (fichiers de résultats)
- `*.pkl`, `*.pkl.gz` (fichiers pickle)
- `corpus/`, `corpus1/`, `corpus2/`, `corpus_tp2/` (corpus générés)
- `.env` (clés API)
- `*.log` (logs)

## Configuration Git (optionnel)

Si vous n'avez pas encore configuré Git :

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

## Structure finale sur GitHub

```
ri/
├── README.md                    # README principal
├── LICENSE                      # Licence MIT
├── .gitignore                   # Fichiers à ignorer
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD (optionnel)
├── tp_indexation/
│   ├── README.md
│   ├── RAPPORT_TP_INDEXATION.md
│   ├── DOCUMENTATION_CODE.md
│   ├── *.py
│   ├── requirements.txt
│   └── .gitignore
└── tp2_modeles/
    ├── README.md
    ├── RAPPORT_COMPLET_TP2.md
    ├── *.py
    ├── requirements.txt
    └── .gitignore
```

## Commandes utiles

```bash
# Voir les fichiers ignorés
git status --ignored

# Voir les différences avant de commit
git diff

# Voir l'historique
git log --oneline

# Ajouter un fichier spécifique
git add nom_du_fichier

# Annuler un ajout
git reset nom_du_fichier
```

