# Etape 1 : Image de base
FROM python:3.11-slim

# Etape 2 : Dossier de travail
WORKDIR /app

# Etape 3 : Copie des fichiers
COPY requirements.txt .
COPY main.py .

# Etape 4 : Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Etape 5 : Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]