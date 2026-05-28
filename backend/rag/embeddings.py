# =========================================================
# embeddings.py
# =========================================================

from sentence_transformers import (
    SentenceTransformer
)

print(
    "\nLoading UniXcoder embedding model...\n"
)

# =========================================================
# EMBEDDING MODEL
# =========================================================

embedding_model = SentenceTransformer(
    "microsoft/unixcoder-base"
)