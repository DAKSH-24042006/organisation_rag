import numpy as np

from rank_bm25 import BM25Okapi

from sentence_transformers import (
    CrossEncoder
)

from rag.embeddings import (
    embedding_model
)

from rag.indexer import (

    client,
    COLLECTION_NAME,
    build_documents,
    code_chunks
)

# =========================================================
# RERANKER
# =========================================================

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

bm25 = None

# =========================================================
# INITIALIZE BM25
# =========================================================

def initialize_bm25():

    global bm25

    documents, bm25_corpus = build_documents()

    bm25 = BM25Okapi(
        bm25_corpus
    )

# =========================================================
# QUERY FILTERS
# =========================================================

def detect_query_filters(query):

    query = query.lower()

    filters = {}

    if any(word in query for word in [

        "react",
        "component",
        "dashboard",
        "frontend",
        "jsx",
        "tsx"

    ]):

        filters["frontend"] = True

    if any(word in query for word in [

        "api",
        "backend",
        "database",
        "service"

    ]):

        filters["backend"] = True

    return filters

# =========================================================
# APPLY METADATA FILTERS
# =========================================================

def apply_metadata_filters(

    results,
    filters
):

    filtered = []

    for result in results:

        payload = result["payload"]

        if filters.get("frontend"):

            if payload["language"] not in [

                "javascript",
                "typescript"
            ]:

                continue

        filtered.append(result)

    return filtered

# =========================================================
# DENSE RETRIEVAL
# =========================================================

def dense_retrieval(

    query,
    top_k=20
):

    query_embedding = embedding_model.encode(
        query
    )

    results = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_embedding.tolist(),

        limit=top_k

    ).points

    dense_results = []

    for result in results:

        dense_results.append({

            "payload":
            result.payload,

            "score":
            result.score
        })

    return dense_results

# =========================================================
# BM25 RETRIEVAL
# =========================================================

def bm25_retrieval(

    query,
    top_k=20
):

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked_indices = np.argsort(
        scores
    )[::-1][:top_k]

    results = []

    for idx in ranked_indices:

        results.append({

            "payload":
            code_chunks[idx],

            "score":
            scores[idx]
        })

    return results

# =========================================================
# HYBRID FUSION
# =========================================================

def hybrid_fusion(

    dense_results,
    bm25_results
):

    combined = {}

    for result in dense_results:

        key = (
            result["payload"]["path"]
            +
            result["payload"]["name"]
        )

        combined[key] = result

    for result in bm25_results:

        key = (
            result["payload"]["path"]
            +
            result["payload"]["name"]
        )

        if key not in combined:

            combined[key] = result

    return list(
        combined.values()
    )

# =========================================================
# RERANKING
# =========================================================

def rerank_results(

    query,
    results,
    top_k=5
):

    pairs = []

    for result in results:

        pairs.append((

            query,

            result["payload"]["content"]
        ))

    scores = reranker.predict(
        pairs
    )

    reranked = []

    for result, score in zip(

        results,
        scores
    ):

        reranked.append({

            "payload":
            result["payload"],

            "score":
            float(score)
        })

    reranked.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    return reranked[:top_k]

# =========================================================
# MAIN RETRIEVAL
# =========================================================

def retrieve(query):

    global bm25

    if bm25 is None:

        initialize_bm25()

    filters = detect_query_filters(
        query
    )

    dense_results = dense_retrieval(
        query
    )

    bm25_results = bm25_retrieval(
        query
    )

    hybrid_results = hybrid_fusion(

        dense_results,
        bm25_results
    )

    filtered_results = apply_metadata_filters(

        hybrid_results,
        filters
    )

    reranked_results = rerank_results(

        query,
        filtered_results
    )

    return reranked_results