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

    # ==========================================
    # NORMALIZE VECTOR SCORES
    # ==========================================

    vector_scores = [
        chunk.get(
            "vector_score",
            0
        )
        for chunk in vector_results
    ]

    v_min = min(vector_scores) if vector_scores else 0
    v_max = max(vector_scores) if vector_scores else 1

    # ==========================================
    # NORMALIZE BM25 SCORES
    # ==========================================

    bm25_scores = [
        chunk.get(
            "bm25_score",
            0
        )
        for chunk in bm25_results
    ]

    b_min = min(bm25_scores) if bm25_scores else 0
    b_max = max(bm25_scores) if bm25_scores else 1

    # ==========================================
    # VECTOR RESULTS
    # ==========================================

    for chunk in vector_results:

        key = (
            chunk["path"]
            +
            chunk["name"]
        )

        score = chunk.get(
            "vector_score",
            0
        )

        if v_max > v_min:

            score = (
                score - v_min
            ) / (
                v_max - v_min
            )

        else:

            score = 1.0

        merged[key] = chunk

        merged[key][
            "hybrid_score"
        ] = (
            score * 0.6
        )

    # ==========================================
    # BM25 RESULTS
    # ==========================================

    for chunk in bm25_results:

        key = (
            chunk["path"]
            +
            chunk["name"]
        )

        score = chunk.get(
            "bm25_score",
            0
        )

        if b_max > b_min:

            score = (
                score - b_min
            ) / (
                b_max - b_min
            )

        else:

            score = 1.0

        if key not in merged:

            merged[key] = chunk

            merged[key][
                "hybrid_score"
            ] = 0

        merged[key][
            "hybrid_score"
        ] += (
            score * 0.4
        )

    results = list(
        merged.values()
    )

    results.sort(
        key=lambda x: x[
            "hybrid_score"
        ],
        reverse=True
    )

    return results



# =========================================================
# CALL GRAPH EXPANSION
# =========================================================

def expand_call_graph(
    chunks,
    max_neighbors=10
):

    lookup = build_symbol_lookup()

    IGNORE_SYMBOLS = {
        "len",
        "str",
        "int",
        "float",
        "dict",
        "list",
        "set",
        "tuple",
        "print",
        "Exception",
        "ValueError",
        "TypeError",
        "RuntimeError",
        "APIRouter",
        "router"
    }



    expanded = []

    seen = set()

    for chunk in chunks:

        key = (
            chunk.get("path","")
            +
            chunk.get("name","")
        )

        if key not in seen:

            expanded.append(chunk)
            seen.add(key)

        calls = chunk.get(
            "calls",
            []
        )

        for call in calls:

            if call in IGNORE_SYMBOLS:
                continue

            if call not in lookup:
                continue

            neighbor = lookup[call]

            nkey = (
                neighbor.get("path","")
                +
                neighbor.get("name","")
            )

            if nkey in seen:
                continue

            neighbor=neighbor.copy()

            neighbor["vector_score"] = (
                chunk.get(
                    "vector_score",
                    0
                ) * 0.95
            )

            expanded.append(
                neighbor
            )

            seen.add(
                nkey
            )

            if len(expanded) >= max_neighbors:
                return expanded

    return expanded


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
# SYMBOL LOOKUP
# =========================================================

def build_symbol_lookup():

    _ensure_initialized()

    lookup = {}

    for chunk in code_chunks:

        name = chunk.get(
            "name",
            ""
        )

        if not name:
            continue

        lookup[name] = chunk

    return lookup


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

    expanded = expand_call_graph(
        merged[:3
               ]
    )

    reranked = rerank_results(
        query,
        expanded,
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