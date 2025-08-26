import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from data_cleaning import get_volumes_datas  # Import propre

# Charger les variables d'environnement
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Charger le modèle de vectorisation
model = SentenceTransformer("all-MiniLM-L6-v2")  # vecteurs de 384 dimensions

# Connexion à la base
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    sslmode="require"
)
cur = conn.cursor()

# Récupération des données depuis data_cleaning.py
volumes_datas = get_volumes_datas()

# Vectorisation et insertion
for item in volumes_datas:
    for filename, volume_data in item.items():
        try:
            content = volume_data["content"]
            embedding = model.encode(content).tolist()

            cur.execute(
                "INSERT INTO documents (id, content, embedding) VALUES (%s, %s, %s)",
                (volume_data["id"], content, embedding)
            )
            print(f"ok ======>>>> {volume_data["id"]}")
        except Exception as e:
            print(f"Erreur pour {filename} : {e}")

conn.commit()
cur.close()
conn.close()
print("Tous les documents ont été vectorisés et insérés.")
