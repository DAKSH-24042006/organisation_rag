from sentence_transformers import (
    SentenceTransformer
)

from rag.config import EMBEDDING_MODEL

print("\nLoading the embedding model...\n")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)