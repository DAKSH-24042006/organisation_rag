# =========================================================
# V2 RERANKER MODULE
# =========================================================

from sentence_transformers import CrossEncoder
from rag.config import RERANKER_MODEL_NAME

_RERANKER = None

def get_reranker_model():
    """Lazily load and return the CrossEncoder reranker model."""
    global _RERANKER
    if _RERANKER is None:
        print(f"\n[INFO] Loading Reranker Model '{RERANKER_MODEL_NAME}'...")
        _RERANKER = CrossEncoder(RERANKER_MODEL_NAME)
        print("[INFO] Reranker Model loaded successfully.\n")
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