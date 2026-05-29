# =========================================================
# CROSS ENCODER RERANKER
# =========================================================

from sentence_transformers import (
    CrossEncoder
)

# =========================================================
# MODEL
# =========================================================

print(
    "\nLoading CrossEncoder reranker...\n"
)

reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# =========================================================
# BUILD CHUNK TEXT
# =========================================================

def build_chunk_text(chunk):

    return f"""
Name:
{chunk.get('name', '')}

Business Role:
{chunk.get('business_role', '')}

Semantic Tags:
{' '.join(chunk.get('semantic_tags', []))}

Summary:
{chunk.get('summary', '')}

Code:
{chunk.get('content', '')[:2000]}
"""

# =========================================================
# RERANK
# =========================================================

def rerank_results(

    query,
    retrieved_chunks,
    top_k=10

):

    if len(retrieved_chunks) == 0:

        return []

    pairs = []

    for chunk in retrieved_chunks:

        chunk_text = build_chunk_text(
            chunk
        )

        pairs.append(

            (
                query,
                chunk_text
            )
        )

    scores = reranker_model.predict(
        pairs
    )

    reranked = []

    for chunk, score in zip(

        retrieved_chunks,
        scores

    ):

        chunk[
            "rerank_score"
        ] = float(score)

        reranked.append(chunk)

    reranked = sorted(

        reranked,

        key=lambda x: x[
            "rerank_score"
        ],

        reverse=True
    )

    return reranked[:top_k]

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_query = (
        "jwt authentication flow"
    )

    sample_chunks = [

        {

            "name":
            "verify_token",

            "summary":
            "Validates JWT token.",

            "semantic_tags":
            [
                "authentication",
                "jwt"
            ],

            "content":
            "def verify_token(): pass"
        }
    ]

    results = rerank_results(

        sample_query,

        sample_chunks
    )

    print(results)