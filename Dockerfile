# Dockerfile pour l'application Django BookSync
FROM python:3.12-alpine

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY='django-insecure-=3h%(r6kdheydgdv1oju0gvvc%h784^dkt0r!aa74$e-=hq6z*'
ENV DEBUG=1
ENV DB_NAME=booksync
ENV DB_USER=booksyncadmin
ENV DB_PASSWORD=wevzuh-paGwi6-nanwag
ENV DB_HOST=bdd-booksync.postgres.database.azure.com
ENV DB_PORT=5432

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copier le code de l'application
COPY book_sync .

# Exposer le port 80 pour la production test
EXPOSE 80

# Commande par défaut (forme exec pour les bonnes pratiques)
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${CONTAINER_APP_PORT}"]
