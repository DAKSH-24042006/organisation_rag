from sentence_transformers import (
    SentenceTransformer
)

from rag.config import (
    EMBEDDING_MODEL
)

print(
    "\nLoading embedding model...\n"
)

from sentence_transformers import SentenceTransformer
from rag.config import EMBEDDING_MODEL

print("\nLoading embedding model...\n")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print(
    "Embedding dimension:",
    embedding_model.get_sentence_embedding_dimension()
)