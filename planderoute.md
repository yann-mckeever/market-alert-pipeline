# Plan de route globale du projet

## Etape 1 - Initialisation de la base de données SQL & Environnement Docker
- Mise en Place de la structure de données
- Configuration du fichier docker-compose.yml pour lancer une base de données PostgreSQL
- Création du schéma SQL pour acceuillir les données et prédiciton

## Etape 2 - Développement des scripts d'Ingestion & ML 
- Ecriture du script d'extraction des données financières via l'API, et insertion SQL via SQLAlchemy
- Developpement du script de traitement des données (features avec Pandas) et de détection d'anomalies (scikit-learn)

## Etape 2 - Conteneurisation de la brique Python
- Création du Dockerfile pour le code python
- Intégration du script dans docker-compose.yml pour s'assurer que Python et PostgreSQL communiquent parfaitement dans le réseau Docker


## Etape 4 - Orchestration avec Apache Airflow
- Ajout d'Airflow dans l'environnement Docker
- Ecriture du DAG pour planifier et lier les tâches d'ingestion et de ML

## Etape 5 - Documentation et Valorisation 
- Rédaction d'un fichier README.md décrivant l'architecture et la commande pour tout lancer

