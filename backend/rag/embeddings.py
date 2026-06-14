# =========================================================
# V2 EMBEDDING MODEL MODULE
# =========================================================

from sentence_transformers import SentenceTransformer
from rag.config import EMBEDDING_MODEL_NAME

_MODEL = None

def get_embedding_model():
    """Lazily load and return the SentenceTransformer model with GPU auto-detection."""
    global _MODEL
    if _MODEL is None:
        import torch
        device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        try:
            print(f"\n[INFO] Loading Embedding Model '{EMBEDDING_MODEL_NAME}' on {device.upper()}...")
            _MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
            _MODEL.max_seq_length = 512
            print(f"[INFO] Embedding dimension: {_MODEL.get_embedding_dimension()}\n")
        except Exception as e:
            print(f"[ERROR] Failed to load embedding model online: {e}")
            print("[INFO] Attempting to load embedding model from local cache (offline mode).")
            try:
                _MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True, device=device)
                _MODEL.max_seq_length = 512
                print(f"[INFO] Embedding Model loaded from cache successfully. Dimension: {_MODEL.get_embedding_dimension()}\n")
            except Exception as e2:
                raise RuntimeError(f"Unable to load embedding model both online and offline: {e2}") from e2
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