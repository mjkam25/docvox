FROM python:3.11-slim

WORKDIR /app

# Copie d'abord les dépendances pour optimiser le cache Docker
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste (main.py, etc.)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]