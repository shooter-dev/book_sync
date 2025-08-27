import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from typing import List

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

model = SentenceTransformer("all-MiniLM-L6-v2")

def encode_text(text: str) -> List[float]:
    return model.encode(text).tolist()

def retrieve_similar_documents(query_embedding: List[float], top_k: int = 5) -> List[dict]:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT content
        FROM documents
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
    """, (query_embedding, top_k))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"content": row[0]} for row in rows]
