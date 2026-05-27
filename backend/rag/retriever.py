import time
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

from rag.config import TOP_K

# =========================================================
# LOAD CROSS ENCODER
# =========================================================

print("\nLoading reranker model...\n")

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# =========================================================
# BM25 PLACEHOLDER
# =========================================================

bm25 = None

# =========================================================
# INITIALIZE BM25
# =========================================================

def initialize_bm25():

    global bm25

    documents, bm25_corpus = build_documents()

    if len(bm25_corpus) == 0:

        raise ValueError(
            "BM25 corpus is empty. "
            "Index repositories first."
        )

    bm25 = BM25Okapi(
        bm25_corpus
    )

    print(
        "\nBM25 initialized successfully.\n"
    )

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

    global bm25

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked_indices = np.argsort(
        scores
    )[::-1][:top_k]

    bm25_results = []

    for idx in ranked_indices:

        bm25_results.append({

            "payload":
            code_chunks[idx],

            "score":
            scores[idx]
        })

    return bm25_results

# =========================================================
# HYBRID FUSION
# =========================================================

def hybrid_fusion(

    dense_results,
    bm25_results,

    dense_weight=0.7,
    bm25_weight=0.3
):

    hybrid_results = {}

    # =====================================================
    # DENSE RESULTS
    # =====================================================

    for result in dense_results:

        key = (
            result["payload"]["path"]
            +
            result["payload"]["name"]
        )

        hybrid_results[key] = {

            "payload":
            result["payload"],

            "score":
            result["score"] * dense_weight
        }

    # =====================================================
    # BM25 RESULTS
    # =====================================================

    for result in bm25_results:

        key = (
            result["payload"]["path"]
            +
            result["payload"]["name"]
        )

        if key in hybrid_results:

            hybrid_results[key]["score"] += (

                result["score"]
                *
                bm25_weight
            )

        else:

            hybrid_results[key] = {

                "payload":
                result["payload"],

                "score":
                result["score"] * bm25_weight
            }

    results = list(
        hybrid_results.values()
    )

    results.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    return results

# =========================================================
# RERANK RESULTS
# =========================================================

def rerank_results(

    query,
    hybrid_results,
    top_k=5
):

    print("\nReranking results...\n")

    pairs = []

    for result in hybrid_results:

        chunk_text = result[
            "payload"
        ]["content"]

        pairs.append(
            (query, chunk_text)
        )

    rerank_scores = reranker.predict(
        pairs
    )

    reranked = []

    for result, score in zip(

        hybrid_results,
        rerank_scores

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
# CONTEXT COMPRESSION
# =========================================================

def compress_context(results):

    compressed = []

    for result in results:

        payload = result["payload"]

        compressed.append(f'''

Repository:
{payload['repo_name']}

File:
{payload['file']}

Type:
{payload['type']}

Name:
{payload['name']}

Code:
{payload['content']}
''')

    return "\n".join(compressed)

# =========================================================
# MAIN RETRIEVAL PIPELINE
# =========================================================

def retrieve(query):

    global bm25

    if bm25 is None:

        initialize_bm25()

    start_time = time.time()

    print("\nRunning dense retrieval...\n")

    dense_results = dense_retrieval(
        query
    )

    print("Running BM25 retrieval...\n")

    bm25_results = bm25_retrieval(
        query
    )

    print("Running hybrid fusion...\n")

    hybrid_results = hybrid_fusion(

        dense_results,
        bm25_results
    )

    print("Running reranking...\n")

    reranked_results = rerank_results(

        query,
        hybrid_results,
        top_k=TOP_K
    )

    retrieval_time = (
        time.time() - start_time
    )

    print(
        f"\nRetrieval completed "
        f"in {retrieval_time:.2f}s"
    )

    print("\nTOP RETRIEVED CHUNKS:\n")

    for result in reranked_results:

        payload = result["payload"]

        print(

            f"{payload['name']} "

            f"({payload['type']}) "

            f"-> Score: "

            f"{result['score']:.4f}"
        )

    context = compress_context(
        reranked_results
    )

    return context