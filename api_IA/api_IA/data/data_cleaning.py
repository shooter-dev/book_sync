import psycopg2
import uuid
import os
import re
from pathlib import Path
from unidecode import unidecode
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

script_dir = Path(__file__).resolve().parent
project_dir = script_dir.parents[2]
output_dir = project_dir / "data_doc" / "fixtures" / "volumes_rag" / "decoupage"
output_dir.mkdir(parents=True, exist_ok=True)

def normalize(text):
    text = unidecode(text.lower().replace(" ", "_"))
    return re.sub(r'[^a-zA-Z0-9_]', '', text)

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cur = conn.cursor()

query = """
SELECT s.title AS serie,
       g.title AS genre,
       STRING_AGG(k.title, ', ') AS kinds,
       v.id as volume_id,
       v.number as volume_number,
       v.content
FROM collection_volume AS v 
LEFT JOIN collection_serie AS s ON v.serie_id = s.id
LEFT JOIN collection_genre AS g ON s.genre_id = g.id
LEFT JOIN collection_serie_kinds AS sk ON s.id = sk.serie_id
LEFT JOIN collection_kind AS k ON sk.kind_id = k.id
WHERE v.content <> '...'
GROUP BY v.id, v.number, v.content, s.title, g.title
ORDER BY serie, v.number ASC NULLS LAST;
"""

cur.execute(query)
rows = cur.fetchall()
volumes_datas: list = []

for row in rows:
    serie, genre, kinds, volume_id, volume_number, content = row

    volume_uuid = str(uuid.uuid4())

    serie_norm = normalize(serie)
    genre_norm = normalize(genre)
    kinds_list = [k.strip() for k in kinds.split(",")] if kinds else []
    kinds_norm = [normalize(k) for k in kinds_list]

    volume_data = {
        "id": volume_uuid,
        "serie": serie,
        "genres": [genre],
        "kinds": kinds_list,
        "volume_number": volume_number,
        "content": content,
        "metadata": {
            "serie_normalized": f"{serie_norm}_{str(volume_number).zfill(3)}",
            "genres_normalized": [genre_norm],
            "kinds_normalized": kinds_norm
        }
    }

    filename = f"{serie_norm}_volume_{volume_number}"
    volumes_datas.append({filename: volume_data})

def get_volumes_datas():
    return volumes_datas
