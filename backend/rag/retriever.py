# =========================================================
# V2 HYBRID GRAPH-AWARE RETRIEVER MODULE
# =========================================================

import os
import json
import numpy as np
from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient
import re

from rag.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    TOP_K,
    RRF_K,
    INDEX_PATH,
    GRAPH_PATH,
    QDRANT_DB_PATH
)
from rag.embeddings import embed_text
from rag.reranker import rerank_results
from rag.graph_database import GraphDatabase

# =========================================================
# LAZY INITIALIZATION FOR CORPUS & BM25
# =========================================================

_CHUNKS = None
_CHUNKS_BY_ID = {}
_BM25_INDEX = None
_GRAPH_DB = None
_QDRANT_CLIENT = None

def _get_qdrant_client():
    global _QDRANT_CLIENT
    if _QDRANT_CLIENT is None:
        try:
            # Try connection to Qdrant server
            _QDRANT_CLIENT = QdrantClient(
                host=QDRANT_HOST,
                port=QDRANT_PORT,
                timeout=3.0
            )
            _QDRANT_CLIENT.get_collections()
        except Exception:
            # Fallback to local disk-based Qdrant client
            _QDRANT_CLIENT = QdrantClient(path=QDRANT_DB_PATH)
    return _QDRANT_CLIENT

def _ensure_initialized():
    global _CHUNKS, _CHUNKS_BY_ID, _BM25_INDEX, _GRAPH_DB
    if _BM25_INDEX is not None:
        return

    # 1. Load Graph Database
    _GRAPH_DB = GraphDatabase()
    if os.path.exists(GRAPH_PATH):
        _GRAPH_DB.load_from_json(GRAPH_PATH)

    # 2. Load Repository Chunks
    if not os.path.exists(INDEX_PATH):
        print(f"[WARNING] Repository index not found at '{INDEX_PATH}'. Running empty retrieval.")
        _CHUNKS = []
        _CHUNKS_BY_ID = {}
        _BM25_INDEX = BM25Okapi([["dummy"]])
        return

    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            _CHUNKS = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load index at '{INDEX_PATH}': {e}")
        _CHUNKS = []
        
    _CHUNKS_BY_ID = {}
    bm25_corpus = []
    
    for chunk in _CHUNKS:
        cid = chunk.get("id")
        if cid:
            _CHUNKS_BY_ID[cid] = chunk
            
        # Tokenize content for BM25 (lowercased words)
        text = f"{chunk.get('name', '')} {chunk.get('type', '')} {chunk.get('path', '')} {chunk.get('content', '')}"
        bm25_corpus.append(text.lower().split())

    if bm25_corpus:
        _BM25_INDEX = BM25Okapi(bm25_corpus)
    else:
        _BM25_INDEX = BM25Okapi([["dummy"]])

# =========================================================
# QUERY UNDERSTANDING / CLASSIFICATION
# =========================================================

def classify_query(query: str) -> str:
    """Classifies user queries into specific code understanding types."""
    q = query.lower()
    
    # 0. File Recovery / Full File Code Queries
    if any(k in q for k in ["get full code", "get the full code", "full code", "entire code", "show code", "show the code", "full content", "read file", "code from file", "view file", "entire file", "code of"]):
        return "FILE_RECOVERY"
        
    # 1. Architecture Queries
    if any(k in q for k in ["architecture", "design", "structure", "components", "modules", "overview", "how it works"]):
        return "ARCHITECTURE"
        
    # 2. Dependency Queries
    if any(k in q for k in ["depend", "import", "who calls", "used by", "calls this", "relationship", "predecessor", "successor"]):
        return "DEPENDENCY"
        
    # 3. Flow Queries
    if any(k in q for k in ["flow", "trace", "execution path", "happen after", "sequence", "pipeline"]):
        return "FLOW"
        
    # 4. Configuration Queries
    if any(k in q for k in ["config", "settings", "yaml", "yml", ".env", "port", "host", "database url", "environment"]):
        return "CONFIGURATION"
        
    # 5. Symbol lookup (exact function/class lookups)
    if any(k in q for k in ["where is", "find class", "find function", "locate class", "locate function", "definition of"]):
        return "SYMBOL"
        
    return "GENERAL"

# =========================================================
# RETRIEVAL IMPLEMENTATIONS
# =========================================================

def vector_search(query: str, top_k: int = 20) -> list:
    """Search Qdrant using dense embeddings."""
    _ensure_initialized()
    try:
        client = _get_qdrant_client()
        query_vector = embed_text(query)
        
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k
        )
        
        output = []
        for point in results.points:
            payload = point.payload
            # Map storage attributes to standard chunk fields
            payload["vector_score"] = point.score
            output.append(payload)
        return output
    except Exception as e:
        print(f"[WARNING] Vector search failed: {e}")
        return []

def bm25_search(query: str, top_k: int = 20) -> list:
    """Search using local BM25Okapi."""
    _ensure_initialized()
    if not _CHUNKS or _BM25_INDEX is None:
        return []
        
    scores = _BM25_INDEX.get_scores(query.lower().split())
    ranked_indices = np.argsort(scores)[::-1]
    
    results = []
    for idx in ranked_indices[:top_k]:
        if scores[idx] <= 0:
            continue
        chunk = _CHUNKS[idx].copy()
        chunk["bm25_score"] = float(scores[idx])
        results.append(chunk)
    return results

def graph_exact_search(query: str) -> list:
    """Looks up exact matches in the NetworkX graph nodes."""
    _ensure_initialized()
    if not _GRAPH_DB:
        return []
        
    results = []
    # Extract words that could represent symbol names
    words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", query)
    
    for word in words:
        # Check if word is a node in the graph (or a suffix match)
        for node_id in _GRAPH_DB.g.nodes:
            if word == node_id or node_id.endswith(f"::{word}") or node_id.endswith(f".{word}"):
                chunk = _CHUNKS_BY_ID.get(node_id)
                if chunk:
                    chunk_copy = chunk.copy()
                    chunk_copy["graph_exact"] = True
                    results.append(chunk_copy)
    return results

def graph_file_recovery_search(query: str) -> list:
    """If a file name is detected, fetch the file node and all its defined symbols from the graph."""
    _ensure_initialized()
    if not _GRAPH_DB:
        return []
        
    results = []
    q_lower = query.lower()
    
    # Check if any file node's path or name is mentioned in the query
    for node_id, ndata in _GRAPH_DB.g.nodes(data=True):
        if ndata.get("type") == "FILE":
            rel_path = ndata.get("file_path", "").lower()
            filename = ndata.get("name", "").lower()
            
            # Match path or simple base name (e.g. "api.py" or "src/api.py")
            if rel_path in q_lower or (filename and filename in q_lower):
                # 1. Fetch the file chunk itself
                file_chunk = _CHUNKS_BY_ID.get(node_id)
                if file_chunk:
                    chunk_copy = file_chunk.copy()
                    chunk_copy["graph_exact"] = True
                    results.append(chunk_copy)
                    
                # 2. Walk outgoing defines / contains edges in the graph to find symbols in this file
                for succ in _GRAPH_DB.g.successors(node_id):
                    edge_data = _GRAPH_DB.g.get_edge_data(node_id, succ)
                    relation = edge_data.get("relation", "")
                    if relation in {"defines", "contains"}:
                        symbol_chunk = _CHUNKS_BY_ID.get(succ)
                        if symbol_chunk:
                            chunk_copy = symbol_chunk.copy()
                            chunk_copy["graph_exact"] = True
                            results.append(chunk_copy)
                break
    return results

# =========================================================
# HYBRID RRF MERGE
# =========================================================

def reciprocal_rank_fusion(vector_res: list, bm25_res: list, exact_res: list) -> list:
    """Applies Reciprocal Rank Fusion (RRF) to combine rankers."""
    scores = {}
    chunks_map = {}
    
    # helper to process ranks
    def add_ranks(results_list):
        for rank, chunk in enumerate(results_list, 1):
            cid = chunk.get("id")
            if not cid:
                continue
            chunks_map[cid] = chunk
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (RRF_K + rank))
            
    add_ranks(vector_res)
    add_ranks(bm25_res)
    add_ranks(exact_res)
    
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    fused_results = []
    for cid in sorted_ids:
        chunk = chunks_map[cid].copy()
        chunk["rrf_score"] = scores[cid]
        fused_results.append(chunk)
        
    return fused_results

# =========================================================
# GRAPH EXPANSION
# =========================================================

def expand_retrieved_graph(fused_chunks: list, max_seeds: int = 5, max_neighbors: int = 15) -> list:
    """Takes top seed chunks, queries NetworkX graph neighbors, and aggregates chunks."""
    _ensure_initialized()
    if not _GRAPH_DB:
        return fused_chunks
        
    expanded_chunks = list(fused_chunks)
    seen_ids = {c["id"] for c in fused_chunks if "id" in c}
    
    # Collect seeds
    seeds = [c["id"] for c in fused_chunks[:max_seeds] if "id" in c]
    
    # Fetch relations
    relations_log = []
    for seed in seeds:
        neighbors = _GRAPH_DB.get_related_neighbors(seed, max_neighbors=max_neighbors)
        for n in neighbors:
            nid = n["node_id"]
            if nid not in seen_ids:
                neighbor_chunk = _CHUNKS_BY_ID.get(nid)
                if neighbor_chunk:
                    chunk_copy = neighbor_chunk.copy()
                    # Apply a small score adjustment for transparency
                    chunk_copy["rrf_score"] = 0.01  # baseline score
                    chunk_copy["graph_expanded"] = True
                    chunk_copy["expanded_relation"] = f"{n['relation']} ({n['direction']}) from {seed.split('::')[-1]}"
                    expanded_chunks.append(chunk_copy)
                    seen_ids.add(nid)
            relations_log.append(f"{seed.split('::')[-1]} --[{n['relation']}]--> {nid.split('::')[-1]}")
            
    # Save graph relationships temporarily on the result list for UI rendering
    for chunk in expanded_chunks:
        chunk["graph_relationships"] = relations_log
        
    return expanded_chunks

# =========================================================
# MAIN RETRIEVAL ENTRY POINT
# =========================================================

def retrieve(query: str, top_k: int = TOP_K) -> dict:
    """Full RAG V2 Retrieval Flow."""
    _ensure_initialized()
    
    # 1. Query pre-classification
    query_type = classify_query(query)
    
    # 2. Adjust candidate pools based on query classification
    vector_k = 20
    bm25_k = 20
    
    if query_type == "CONFIGURATION":
        # Prioritize config filenames and terms
        query = f"config yaml settings env {query}"
        bm25_k = 30
    elif query_type == "ARCHITECTURE":
        # Prioritize high-level files and READMEs
        query = f"architecture overview layout components README {query}"
        
    # 3. Retrieve
    v_results = vector_search(query, top_k=vector_k)
    b_results = bm25_search(query, top_k=bm25_k)
    e_results = graph_exact_search(query)
    
    # If it is a FILE_RECOVERY query, perform file-based recovery retrieval
    if query_type == "FILE_RECOVERY":
        file_results = graph_file_recovery_search(query)
        e_results.extend(file_results)
    
    # 4. RRF Rank Fusion
    fused = reciprocal_rank_fusion(v_results, b_results, e_results)
    
    # 5. Graph Neighbors Expansion
    expanded = expand_retrieved_graph(fused, max_seeds=5, max_neighbors=15)
    
    # 6. CrossEncoder Reranking
    reranked = rerank_results(query, expanded, top_k=top_k)
    
    return {
        "query_type": query_type,
        "results": reranked,
        "statistics": {
            "vector_count": len(v_results),
            "bm25_count": len(b_results),
            "exact_count": len(e_results),
            "total_candidates": len(expanded)
        }
    }