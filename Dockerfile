FROM python:3.12-slim

#Dossier de travail dans le conteneur
WORKDIR /app

#Dépendance nécéssaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#Copier le fichier de dépendances 
COPY requirements.txt .

#Installer les bibliothèques python
RUN pip install --no-cache-dir -r requirements.txt

#Copier les scripts dans le conteneur
COPY scripts/ ./scripts/

#Variables d'environnement par défaut
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python","scripts/ingest.py"]
