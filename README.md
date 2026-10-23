# Streamlit app of a Rocket League Data Analysis

## Présentation du projet

Ce projet consiste à développer une application interactive avec **Streamlit** afin d'analyser des données de matchs de Rocket League.

L'objectif est de transformer un jeu de données statistiques en une histoire visuelle et interactive permettant de mieux comprendre les différences entre les équipes gagnantes et perdantes.

À travers différentes visualisations, l'application cherchera à identifier les statistiques associées à la victoire et à explorer les facteurs qui peuvent influencer les performances d'une équipe.

## Objectifs

- Explorer et comprendre les données statistiques de Rocket League.
- Comparer les performances des équipes gagnantes et perdantes.
- Étudier les relations entre les différentes statistiques et les résultats des matchs.
- Identifier des tendances liées à l'attaque, à la défense, à la gestion du boost, à la vitesse, au positionnement et aux interactions physiques.
- Présenter les résultats de manière claire et interactive grâce à une application Streamlit.

## Jeu de données

Le projet utilise le fichier `isaac_train_xG.csv` issu du dépôt GitHub [RL-xG-Predictor](https://github.com/isaactallack/RL-xG-Predictor).

Ce jeu de données contient des statistiques de matchs de Rocket League, notamment :

- **Attaque :** buts et tirs.
- **Défense :** tirs concédés et positionnement défensif.
- **Gestion du boost :** quantité de boost collectée, utilisée ou volée.
- **Déplacements :** vitesse moyenne, distance parcourue et vitesse supersonique.
- **Positionnement :** distance par rapport au ballon et répartition sur le terrain.
- **Interactions physiques :** démolitions infligées et subies.

Les statistiques sont disponibles pour les deux équipes, ce qui permet de comparer leurs performances.

> **Remarque :** les définitions exactes des variables, la méthode de détermination des victoires et défaites ainsi que les éventuelles valeurs manquantes devront être vérifiées avant de tirer des conclusions.

## Structure du projet

```text
rocket-league-analysis/
│
├── app.py
├── requirements.txt
├── README.md
│
├── sections/
│   ├── intro.py
│   ├── overview.py
│   ├── deep_dives.py
│   └── conclusions.py
│
├── utils/
│   ├── io.py
│   ├── prep.py
│   └── viz.py
│
├── data/
│
└── assets/
```

### Organisation des fichiers

- `app.py` : point d'entrée de l'application Streamlit.
- `sections/intro.py` : présentation du projet, contexte, objectifs et limites des données.
- `sections/overview.py` : indicateurs clés et aperçu général des données.
- `sections/deep_dives.py` : analyses détaillées et comparaisons entre équipes.
- `sections/conclusions.py` : synthèse des résultats et principaux enseignements.
- `utils/io.py` : chargement et mise en cache des données.
- `utils/prep.py` : nettoyage, préparation et création des variables nécessaires à l'analyse.
- `utils/viz.py` : fonctions de visualisation réutilisables.
- `data/` : stockage facultatif des données locales ou préparées.
- `assets/` : ressources graphiques utilisées dans l'application.

## Technologies utilisées

- **Python** : traitement et analyse des données.
- **Pandas** : manipulation et préparation des données.
- **Streamlit** : création de l'application interactive.
- **Plotly** : création de graphiques interactifs.

## Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd rocket-league-analysis
```

Remplacer `<URL_DU_DEPOT>` par l'adresse du dépôt Git de ce projet, si celui-ci est hébergé en ligne.

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

Activer ensuite l'environnement virtuel.

**Windows — PowerShell :**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux :**

```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Lancer l'application

Une fois les dépendances installées, lancer la commande suivante depuis le dossier du projet :

```bash
streamlit run app.py
```

L'application s'ouvrira dans le navigateur et permettra d'explorer les analyses interactives.

## Démarche d'analyse

Le projet suivra plusieurs étapes :

1. **Exploration des données :** comprendre les variables, vérifier la qualité des données et repérer les valeurs manquantes.
2. **Préparation :** nettoyer les données et organiser les statistiques des deux équipes afin de permettre des comparaisons cohérentes.
3. **Analyse globale :** présenter les principaux indicateurs et les caractéristiques générales des matchs.
4. **Comparaison des résultats :** étudier les différences entre équipes gagnantes et perdantes.
5. **Approfondissement :** explorer les statistiques les plus intéressantes à l'aide de graphiques interactifs.
6. **Interprétation :** résumer les tendances observées et discuter de leurs limites.

## Limites de l'analyse

Les résultats devront être interprétés avec prudence. Une différence statistique entre équipes gagnantes et perdantes ne démontre pas nécessairement une relation de cause à effet.

Les performances peuvent dépendre de nombreux facteurs qui ne sont pas nécessairement présents dans le jeu de données, tels que le niveau des joueurs, leur coordination, leur stratégie ou le contexte du match.

Les conclusions seront donc formulées à partir des tendances observées dans les données disponibles.

## Résultat attendu

Le résultat final sera une application interactive permettant de naviguer entre une présentation générale des données, des analyses approfondies et une synthèse des principaux enseignements.

L'ambition est de raconter une histoire à partir des statistiques et de mieux comprendre ce qui distingue, dans les données observées, les équipes qui gagnent de celles qui perdent.

## Auteur

Projet réalisé dans le cadre d'un travail d'analyse de données et de développement d'une application interactive.
