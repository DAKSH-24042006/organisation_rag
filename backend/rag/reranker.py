# =========================================================
# V2 RERANKER MODULE
# =========================================================

from sentence_transformers import CrossEncoder
from rag.config import RERANKER_MODEL_NAME

_RERANKER = None

def get_reranker_model():
    """Lazily load and return the CrossEncoder reranker model with GPU auto-detection."""
    global _RERANKER
    if _RERANKER is None:
        import torch
        device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        try:
            print(f"\n[INFO] Loading Reranker Model '{RERANKER_MODEL_NAME}' on {device.upper()}...")
            _RERANKER = CrossEncoder(RERANKER_MODEL_NAME, device=device)
            print("[INFO] Reranker Model loaded successfully.\n")
        except Exception as e:
            # Common issue: offline/no network, or HTTP client closed due to network problems
            print(f"[ERROR] Failed to load reranker model online: {e}")
            print("[INFO] Attempting to load model from local cache (offline mode).")
            try:
                _RERANKER = CrossEncoder(RERANKER_MODEL_NAME, local_files_only=True, device=device)
                print("[INFO] Reranker Model loaded from cache successfully.\n")
            except Exception as e2:
                raise RuntimeError(f"Unable to load reranker model both online and offline: {e2}") from e2
    return _RERANKER

def rerank_results(query: str, chunks: list, top_k: int = 10) -> list:
    """Rerank candidates against the query using cross-encoder."""
    if not chunks:
        return []
        
    model = get_reranker_model()
    pairs = []
    for chunk in chunks:
        # Build text description of chunk content
        chunk_text = f"File: {chunk.get('file', '')} | Type: {chunk.get('type', '')} | Name: {chunk.get('name', '')}\nCode:\n{chunk.get('content', '')}"
        pairs.append((query, chunk_text))
        
    scores = model.predict(pairs)
    
    reranked = []
    for chunk, score in zip(chunks, scores):
        updated_chunk = chunk.copy()
        updated_chunk["rerank_score"] = float(score)
        reranked.append(updated_chunk)
        
    # Sort descending
    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]