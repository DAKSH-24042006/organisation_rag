from sentence_transformers import (
    SentenceTransformer
)

# =========================================================
# CODE EMBEDDING MODEL
# =========================================================

EMBEDDING_MODEL = (
    "BAAI/bge-small-en-v1.5"
)

print("\nLoading embedding model...\n")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)