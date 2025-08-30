# Dockerfile pour l'application Django BookSync
FROM python:3.12-alpine

# Variables d'environnement
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc musl-dev postgresql-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copier le code de l'application
COPY book_sync .

# Exposer le port 80 pour la production test
EXPOSE 80

# Commande par défaut (forme exec pour les bonnes pratiques)
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${CONTAINER_APP_PORT}"]
