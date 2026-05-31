# =========================================================
# UNIVERSAL CODE RERANKER
# =========================================================

from sentence_transformers import CrossEncoder

print("\nLoading Code Reranker...\n")

reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# =========================================================
# BUILD CHUNK TEXT
# =========================================================

def build_chunk_text(chunk):

    return f"""
Repository:
{chunk.get("repo_name","")}

Language:
{chunk.get("language","")}

Type:
{chunk.get("type","")}

Name:
{chunk.get("name","")}

File:
{chunk.get("file","")}

Code:
{chunk.get("content","")[:3000]}
"""

# =========================================================
# RERANK
# =========================================================

def rerank_results(
    query,
    chunks,
    top_k=10
):

    if not chunks:
        return []

    pairs = []

    for chunk in chunks:

        pairs.append(
            (
                query,
                build_chunk_text(chunk)
            )
        )

    scores = reranker_model.predict(
        pairs
    )

    reranked = []

    for chunk, score in zip(
        chunks,
        scores
    ):

        chunk["rerank_score"] = float(score)

        reranked.append(chunk)

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]