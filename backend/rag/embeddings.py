# =========================================================
# V2 EMBEDDING MODEL MODULE
# =========================================================

from sentence_transformers import SentenceTransformer
from rag.config import EMBEDDING_MODEL_NAME

_MODEL = None

def get_embedding_model():
    """Lazily load and return the SentenceTransformer model."""
    global _MODEL
    if _MODEL is None:
        print(f"\n[INFO] Loading Embedding Model '{EMBEDDING_MODEL_NAME}'...")
        _MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
        # Standard context limit for all-MiniLM-L6-v2 is 256/512 tokens
        _MODEL.max_seq_length = 512
        print(f"[INFO] Embedding dimension: {_MODEL.get_embedding_dimension()}\n")
    return _MODEL

def embed_text(text: str):
    """Embed a single text string, ensuring truncation."""
    model = get_embedding_model()
    # sentence-transformers encode respects model.max_seq_length set during load
    emb = model.encode([text])
    return emb[0].tolist()

def embed_texts(texts: list):
    """Embed a list of text strings with truncation."""
    if not texts:
        return []
    model = get_embedding_model()
    embs = model.encode(texts, show_progress_bar=False)
    return embs.tolist()