#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_reco.py — Ingestion CSV (44k volumes) + VectorStore Chroma + RAG + Recommandation
LangChain + Azure OpenAI (embeddings + chat)
Correction: nettoyage des métadonnées pour Chroma (pas de listes).
"""

import os
import re
import csv
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple

from dotenv import load_dotenv

# LangChain / OpenAI
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ===========================================
# Utilitaires de nettoyage & normalisation
# ===========================================

ACCENT_MAP = str.maketrans(
    "àáâäæçéèêëîïôöùúûüÿñœÀÁÂÄÆÇÉÈÊËÎÏÔÖÙÚÛÜŸÑŒ",
    "aaaaaceeeeii oouuuynoeAAAAACEEEEIIOOUUUYN OE".replace(" ", "")
)

def slugify(s: str) -> str:
    if s is None:
        return ""
    s = s.strip().translate(ACCENT_MAP).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")

def split_tags(field: str) -> List[str]:
    if field is None:
        return []
    field = field.strip().strip(";")
    parts = [p.strip() for p in re.split(r",\s*", field) if p.strip()]
    return parts

def normalize_tags(tags: List[str]) -> List[str]:
    return [slugify(t) for t in tags if t]

def safe_int(s: str, default: int = 0) -> int:
    try:
        return int(s)
    except Exception:
        return default

# ===========================================
# Nettoyage des métadonnées pour Chroma
# ===========================================

def clean_metadata(metadata: dict) -> dict:
    cleaned = {}
    for k, v in metadata.items():
        if isinstance(v, list):
            cleaned[k] = ", ".join(map(str, v))
        elif isinstance(v, dict):
            cleaned[k] = json.dumps(v, ensure_ascii=False)
        else:
            cleaned[k] = v
    return cleaned

# ===========================================
# Lecture CSV tolérante
# ===========================================

def smart_csv_reader(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    def clean_header(h: str) -> str:
        return h.strip().strip(";").replace('""', '"').strip('"')
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    cleaned = raw.replace('""', '"')
    try:
        lines = cleaned.splitlines()
        if not lines:
            return rows
        headers = [clean_header(h) for h in next(csv.reader([lines[0]]))]
        reader = csv.DictReader(lines[1:], fieldnames=headers)
        for r in reader:
            fixed = {k: (v.strip().strip(";") if isinstance(v, str) else v) for k, v in r.items()}
            rows.append(fixed)
        if rows and all(k in rows[0] and rows[0][k] == k for k in ["serie","genre","kinds","volume_id","volume_number","content"]):
            rows.pop(0)
        return rows
    except Exception:
        pass
    # fallback regex
    fallback = []
    for line in raw.splitlines()[1:]:
        parts = re.findall(r'"(.*?)"', line)
        if len(parts) >= 6:
            fallback.append({
                "serie": parts[0],
                "genre": parts[1],
                "kinds": parts[2],
                "volume_id": parts[3],
                "volume_number": parts[4],
                "content": parts[5],
            })
    return fallback

# ===========================================
# Construction des Documents
# ===========================================

def build_documents(rows: List[Dict[str, str]]) -> List[Document]:
    docs: List[Document] = []
    for r in rows:
        serie = (r.get("serie") or "").strip()
        genre = (r.get("genre") or "").strip()
        kinds = (r.get("kinds") or "").strip()
        volume_id = (r.get("volume_id") or "").strip()
        volume_number_raw = (r.get("volume_number") or "").strip()
        content = (r.get("content") or "").strip()

        genres_list = split_tags(genre)
        kinds_list = split_tags(kinds)

        meta = {
            "id": volume_id,
            "serie": serie,
            "serie_normalized": slugify(serie),
            "genres": genres_list,
            "genres_normalized": normalize_tags(genres_list),
            "kinds": kinds_list,
            "kinds_normalized": normalize_tags(kinds_list),
            "volume_number": safe_int(volume_number_raw),
        }

        # Nettoyage Chroma (pas de listes)
        meta = clean_metadata(meta)

        header = f"Série: {serie}\nGenres: {', '.join(genres_list)}\nThèmes: {', '.join(kinds_list)}\nTome: {meta['volume_number']}\n\n"
        page_content = header + content

        docs.append(Document(page_content=page_content, metadata=meta))
    return docs

# ===========================================
# Embeddings / LLM / VectorStore
# ===========================================

def make_embeddings() -> AzureOpenAIEmbeddings:
    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    if not deployment:
        raise RuntimeError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT manquant")
    return AzureOpenAIEmbeddings(
        azure_deployment=deployment,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )

def make_chat_llm(temperature: float = 0.2) -> AzureChatOpenAI:
    deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
    if not deployment:
        raise RuntimeError("AZURE_OPENAI_CHAT_DEPLOYMENT manquant")
    return AzureChatOpenAI(
        azure_deployment=deployment,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        temperature=temperature,
    )

def get_vectorstore(persist_directory: str, embeddings: AzureOpenAIEmbeddings) -> Chroma:
    return Chroma(
        collection_name="manga_volumes",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

def build_index(csv_path: str, persist_directory: str) -> Tuple[int, int]:
    rows = smart_csv_reader(csv_path)
    if not rows:
        raise RuntimeError("CSV vide ou illisible")
    docs = build_documents(rows)
    embeddings = make_embeddings()
    vs = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="manga_volumes",
        persist_directory=persist_directory
    )
    vs.persist()
    return len(rows), len(docs)

# ===========================================
# Recherche / RAG
# ===========================================

def search(
    query: str,
    persist_directory: str,
    k: int = 5,
    filter_genre: Optional[str] = None,
    include_kinds: Optional[List[str]] = None,
    exclude_kinds: Optional[List[str]] = None,
) -> List[Document]:
    embeddings = make_embeddings()
    vs = get_vectorstore(persist_directory, embeddings)
    chroma_filter: Dict[str, Any] = {}

    if filter_genre:
        chroma_filter["genres_normalized"] = {"$contains": slugify(filter_genre)}
    if include_kinds:
        chroma_filter["kinds_normalized"] = {"$in": [slugify(k) for k in include_kinds]}
    if exclude_kinds:
        chroma_filter["kinds_normalized"] = {"$nin": [slugify(k) for k in exclude_kinds]}

    docs = vs.similarity_search(query, k=k, filter=chroma_filter if chroma_filter else None)
    return docs

def build_rag_chain(persist_directory: str):
    embeddings = make_embeddings()
    vs = get_vectorstore(persist_directory, embeddings)
    retriever = vs.as_retriever(search_kwargs={"k": 5})

    system_prompt = (
        "Vous êtes un assistant de recommandation et d'information sur des séries et leurs volumes. "
        "Répondez en français, de façon concise, en citant les séries et tomes utilisés. "
        "Si l'information est absente du contexte, dites-le clairement."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Question: {question}\n\nContexte:\n{context}")
    ])

    llm = make_chat_llm(temperature=0.2)

    def format_docs(docs: List[Document]) -> str:
        blocks = []
        for d in docs:
            meta = d.metadata
            head = f"- {meta.get('serie')} (Tome {meta.get('volume_number')})"
            blocks.append(head + "\n" + d.page_content[:1200])
        return "\n\n".join(blocks)

    chain = (
        {"question": RunnablePassthrough(), "context": retriever | format_docs}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# ===========================================
# Recommandation simple
# ===========================================

def recommend_books(
    persist_directory: str,
    user_profile: Dict[str, Any],
    k: int = 10
) -> List[Dict[str, Any]]:
    likes_genres = [slugify(g) for g in user_profile.get("like_genres", [])]
    dislikes_genres = [slugify(g) for g in user_profile.get("dislike_genres", [])]
    likes_kinds = [slugify(kd) for kd in user_profile.get("like_kinds", [])]
    dislikes_kinds = [slugify(kd) for kd in user_profile.get("dislike_kinds", [])]

    query_parts = []
    if likes_kinds:
        query_parts.append("Thèmes: " + ", ".join(likes_kinds))
    if likes_genres:
        query_parts.append("Genres: " + ", ".join(likes_genres))
    base_query = "Recherche de séries et tomes pertinents. " + " | ".join(query_parts)

    include_kinds = likes_kinds or None
    docs = search(
        base_query,
        persist_directory=persist_directory,
        k=k*3,
        filter_genre=likes_genres[0] if likes_genres else None,
        include_kinds=include_kinds
    )

    def score_doc(d: Document) -> int:
        s = 0
        for g in likes_genres:
            if g in d.metadata.get("genres_normalized", ""):
                s += 2
        for kd in likes_kinds:
            if kd in d.metadata.get("kinds_normalized", ""):
                s += 1
        return s

    docs_sorted = sorted(docs, key=score_doc, reverse=True)[:k]
    return [{"serie": d.metadata.get("serie"), "volume": d.metadata.get("volume_number")} for d in docs_sorted]

# ===========================================
# CLI
# ===========================================

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="RAG Manga Reco Indexer / Searcher")
    parser.add_argument("--csv", type=str, required=True, help="Chemin vers le CSV")
    parser.add_argument("--persist", type=str, required=True, help="Répertoire Chroma")
    args = parser.parse_args()

    print(f"Indexation du CSV {args.csv}...")
    n_rows, n_docs = build_index(args.csv, args.persist)
    print(f"✅ {n_rows} lignes lues, {n_docs} documents indexés dans {args.persist}")

if __name__ == "__main__":
    main()
