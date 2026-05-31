# =========================================================
# ORGANIZATION RAG RETRIEVER
# =========================================================

import json
import numpy as np

from rank_bm25 import BM25Okapi

from qdrant_client import QdrantClient

from rag.embeddings import (
    embedding_model
)

from rag.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME
)

from rag.reranker import (
    rerank_results
)

# =========================================================
# LAZY INITIALIZATION
# =========================================================

code_chunks = []
bm25 = None

def _ensure_initialized():
    global code_chunks, bm25
    if bm25 is not None:
        return

    import os
    index_path = "data/repository_index.json"
    
    # Try local workspace path if not found
    if not os.path.exists(index_path):
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "repository_index.json")
        if os.path.exists(fallback_path):
            index_path = fallback_path

    if not os.path.exists(index_path):
        print(f"[WARNING] Repository index not found at '{index_path}'. BM25 search will be empty.")
        code_chunks = []
        bm25 = BM25Okapi([["dummy"]])
        return

    try:
        with open(
            index_path,
            "r",
            encoding="utf-8"
        ) as f:
            code_chunks = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load index at '{index_path}': {e}")
        code_chunks = []
        bm25 = BM25Okapi([["dummy"]])
        return

    bm25_corpus = []

    for chunk in code_chunks:

        text = f"""
        {chunk.get("name","")}
        {chunk.get("type","")}
        {chunk.get("language","")}
        {chunk.get("file","")}
        {chunk.get("content","")}
        """

        bm25_corpus.append(
            text.lower().split()
        )

    if bm25_corpus:
        bm25 = BM25Okapi(bm25_corpus)
    else:
        bm25 = BM25Okapi([["dummy"]])

# =========================================================
# QDRANT WITH FALLBACK
# =========================================================

try:
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        timeout=5.0
    )
    # Check connection
    client.get_collections()
except Exception as e:
    # Use exact same local DB fallback as indexer.py
    # Resolve relative to backend/data/qdrant_db if needed
    import os
    db_path = "data/qdrant_db"
    if not os.path.exists("data") and os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "qdrant_db")
    client = QdrantClient(path=db_path)

# =========================================================
# VECTOR SEARCH
# =========================================================

def vector_search(
    query,
    top_k=20
):

    embedding = embedding_model.encode(
        query
    ).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=top_k
    )

    output = []

    for point in results.points:

        payload = point.payload

        payload["vector_score"] = (
            point.score
        )

        output.append(payload)

    return output

# =========================================================
# BM25 SEARCH
# =========================================================

def bm25_search(
    query,
    top_k=20
):

    _ensure_initialized()
    if not code_chunks or bm25 is None:
        return []

    scores = bm25.get_scores(
        query.lower().split()
    )

    ranked = np.argsort(
        scores
    )[::-1]

    results = []

    for idx in ranked[:top_k]:

        chunk = code_chunks[idx].copy()

        chunk["bm25_score"] = float(
            scores[idx]
        )

        results.append(chunk)

    return results

# =========================================================
# HYBRID MERGE
# =========================================================

def hybrid_merge(
    vector_results,
    bm25_results
):

    merged = {}

    for chunk in vector_results:

        key = (
            chunk["path"]
            +
            chunk["name"]
        )

        merged[key] = chunk

        merged[key]["hybrid_score"] = (
            chunk["vector_score"] * 0.7
        )

    for chunk in bm25_results:

        key = (
            chunk["path"]
            +
            chunk["name"]
        )

        if key not in merged:

            merged[key] = chunk

            merged[key]["hybrid_score"] = 0

        merged[key]["hybrid_score"] += (
            chunk["bm25_score"] * 0.3
        )

    results = list(
        merged.values()
    )

    results.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return results

# =========================================================
# CONTEXT BUILDER
# =========================================================

def build_context(
    chunks,
    max_chunks=5
):

    context = ""

    for chunk in chunks[:max_chunks]:

        context += f"""

================================================

Repository:
{chunk.get('repo_name')}

Language:
{chunk.get('language')}

Type:
{chunk.get('type')}

Name:
{chunk.get('name')}

File:
{chunk.get('file')}

Lines:
{chunk.get('start_line')}
-
{chunk.get('end_line')}

Code:

{chunk.get('content')}

================================================

"""

    return context

# =========================================================
# RETRIEVE
# =========================================================

def retrieve(
    query,
    top_k=10
):

    _ensure_initialized()

    vector_results = vector_search(
        query,
        top_k=top_k*2
    )

    bm25_results = bm25_search(
        query,
        top_k=top_k*2
    )

    merged = hybrid_merge(
        vector_results,
        bm25_results
    )

    reranked = rerank_results(
        query,
        merged,
        top_k=top_k
    )

    return build_context(
        reranked
    )

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    query = input(
        "\nQuery: "
    )

    context = retrieve(
        query
    )

    print(context)