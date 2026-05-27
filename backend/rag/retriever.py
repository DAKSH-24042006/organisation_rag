import time
import numpy as np

from rank_bm25 import BM25Okapi

from rag.config import (
    TOP_K,
    COLLECTION_NAME
)

from rag.embeddings import embedding_model

from rag.indexer import (
    client,
    code_chunks,
    build_documents
)

bm25 = None

# =========================================================
# INITIALIZE BM25
# =========================================================

def initialize_bm25():

    global bm25

    documents, bm25_corpus = build_documents()

    bm25 = BM25Okapi(bm25_corpus)

    print("\nBM25 Initialized Successfully.\n")

# =========================================================
# DENSE RETRIEVAL
# =========================================================

def dense_retrieval(query):

    query_embedding = embedding_model.encode(
        [query]
    )

    dense_results = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_embedding[0].tolist(),

        limit=TOP_K

    ).points

    return dense_results

# =========================================================
# BM25 RETRIEVAL
# =========================================================

def bm25_retrieval(query):

    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    bm25_top_indices = np.argsort(
        bm25_scores
    )[-TOP_K:][::-1]

    return bm25_scores, bm25_top_indices

# =========================================================
# HYBRID FUSION
# =========================================================

def hybrid_fusion(
    dense_results,
    bm25_scores,
    bm25_top_indices
):

    hybrid_results = {}

    # =====================================================
    # DENSE
    # =====================================================

    for result in dense_results:

        payload = result.payload

        key = payload["name"] + payload["file"]

        hybrid_results[key] = {

            "score":
            float(result.score) * 0.7,

            "payload":
            payload,

            "source":
            "dense"
        }

    # =====================================================
    # BM25
    # =====================================================

    for idx in bm25_top_indices:

        chunk = code_chunks[idx]

        key = chunk["name"] + chunk["file"]

        bm25_score = float(
            bm25_scores[idx]
        )

        if key in hybrid_results:

            hybrid_results[key]["score"] += (
                bm25_score * 0.3
            )

            hybrid_results[key]["source"] = (
                "hybrid"
            )

        else:

            hybrid_results[key] = {

                "score":
                bm25_score * 0.3,

                "payload":
                chunk,

                "source":
                "bm25"
            }

    final_results = sorted(

        hybrid_results.values(),

        key=lambda x: x["score"],

        reverse=True
    )

    return final_results[:TOP_K]

# =========================================================
# MAIN RETRIEVAL
# =========================================================

def retrieve(query):

    global bm25

    if bm25 is None:

        initialize_bm25()

    start_time = time.time()

    dense_results = dense_retrieval(query)

    bm25_scores, bm25_top_indices = (
        bm25_retrieval(query)
    )

    final_results = hybrid_fusion(

        dense_results,

        bm25_scores,

        bm25_top_indices
    )

    end_time = time.time()

    retrieval_time = (
        end_time - start_time
    )

    print("\n" + "=" * 60)
    print("HYBRID RETRIEVAL METRICS")
    print("=" * 60)

    print(
        f"Retrieval Time: "
        f"{retrieval_time:.4f} seconds"
    )

    return final_results

# =========================================================
# CONTEXT COMPRESSION
# =========================================================

def compress_context(chunks):

    context = ""

    for idx, chunk in enumerate(chunks):

        payload = chunk["payload"]

        context += f'''

==============================
CHUNK {idx+1}
==============================

Repository:
{payload['repo_name']}

Framework:
{payload['framework']}

Architecture:
{payload['architecture']}

Type:
{payload['type']}

Name:
{payload['name']}

Dependencies:
{payload['dependencies']}

Code:
{payload['content']}
'''

    return context