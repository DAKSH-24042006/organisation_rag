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
    QDRANT_DB_PATH,
    REPOSITORIES
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
_SYMBOL_LOOKUP = None

def _get_qdrant_client():
    global _QDRANT_CLIENT
    if _QDRANT_CLIENT is None:
        try:
            # Try connection to Qdrant
            _QDRANT_CLIENT = QdrantClient(
                host=QDRANT_HOST,
                port=QDRANT_PORT,
                timeout=3
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
        
    # Build pre-cached symbol dictionary for O(1) exact lookups
    global _SYMBOL_LOOKUP
    _SYMBOL_LOOKUP = {}
    if _GRAPH_DB:
        for node_id in _GRAPH_DB.g.nodes:
            # Map exact node_id
            _SYMBOL_LOOKUP[node_id.lower()] = node_id
            
            # Map suffix/qualified names
            if "::" in node_id:
                parts = node_id.split("::")
                sym_name = parts[-1]
                _SYMBOL_LOOKUP[sym_name.lower()] = node_id
                if "." in sym_name:
                    _SYMBOL_LOOKUP[sym_name.split(".")[-1].lower()] = node_id
            else:
                # File path node
                _SYMBOL_LOOKUP[node_id.lower()] = node_id
                filename = os.path.basename(node_id).lower()
                _SYMBOL_LOOKUP[filename] = node_id
                name_without_ext = os.path.splitext(filename)[0]
                _SYMBOL_LOOKUP[name_without_ext] = node_id

# =========================================================
# QUERY UNDERSTANDING / CLASSIFICATION
# =========================================================

def classify_query(query: str) -> str:
    """Classifies user queries into specific code understanding types."""
    q = query.lower().strip()
    
    # 0. File Recovery / Full File Code Queries
    if any(k in q for k in ["get full code", "get the full code", "full code", "entire code", "show code", "show the code", "full content", "read file", "code from file", "view file", "entire file", "code of"]):
        return "FILE_RECOVERY"
        
    # 1. Overview / Architectural Queries
    overview_keywords = [
        "architecture", "design", "structure", "components", "modules", "overview", 
        "how it works", "readme", "about this", "layout", "tech stack", 
        "frameworks", "framework", "languages", "summary", "blueprint"
    ]
    if any(k in q for k in overview_keywords):
        return "OVERVIEW"
        
    # Combination checks: e.g. "explain the repo", "explain SBOSS", "explain codebase"
    explain_targets = ["repo", "repository", "codebase", "project", "application", "system"]
    for r in REPOSITORIES:
        name_lower = r["name"].lower()
        explain_targets.append(name_lower)
        if "-" in name_lower:
            explain_targets.append(name_lower.split("-")[0])
        if "_" in name_lower:
            explain_targets.append(name_lower.split("_")[0])
            
    if "explain" in q and any(t in q for t in explain_targets):
        return "OVERVIEW"
    if "what is" in q and any(t in q for t in explain_targets):
        return "OVERVIEW"
    if q in ["explain", "overview", "help", "readme.md"]:
        return "OVERVIEW"
        
    # 2. Debugging / Trace Queries
    debug_keywords = [
        "fail", "error", "debug", "exception", "bug", "trace", "crash", "wrong", 
        "incorrect", "issue", "tokenexpired", "expired", "failed", "broken", 
        "why does", "why is", "fix", "flow", "sequence", "pipeline"
    ]
    if any(k in q for k in debug_keywords):
        return "DEBUG"
        
    # 3. Default to Code Search
    return "CODE_SEARCH"

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
            if payload is not None:
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
    """Looks up exact matches in the pre-cached symbol dictionary."""
    _ensure_initialized()
    if not _GRAPH_DB or not _SYMBOL_LOOKUP:
        return []
        
    results = []
    words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", query)
    
    for word in words:
        word_lower = word.lower()
        if word_lower in _SYMBOL_LOOKUP:
            node_id = _SYMBOL_LOOKUP[word_lower]
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

def expand_debug_graph(fused_chunks: list, max_seeds: int = 5, max_neighbors: int = 15) -> list:
    """Recursively traces callers (incoming) and callees (outgoing) up to depth 2 for top seed nodes."""
    _ensure_initialized()
    if not _GRAPH_DB:
        return fused_chunks
        
    expanded_chunks = list(fused_chunks)
    seen_ids = {c["id"] for c in fused_chunks if "id" in c}
    
    seeds = [c["id"] for c in fused_chunks[:max_seeds] if "id" in c]
    relations_log = []
    
    queue = [(s, 0) for s in seeds]
    visited = set(seeds)
    
    while queue:
        curr, depth = queue.pop(0)
        if depth >= 2:
            continue
            
        if curr in _GRAPH_DB.g:
            # 1. Successors (Callees)
            for succ in _GRAPH_DB.g.successors(curr):
                edge_data = _GRAPH_DB.g.get_edge_data(curr, succ)
                relation = edge_data.get("relation", "")
                if relation == "calls" and succ not in visited:
                    visited.add(succ)
                    neighbor_chunk = _CHUNKS_BY_ID.get(succ)
                    if neighbor_chunk:
                        chunk_copy = neighbor_chunk.copy()
                        chunk_copy["rrf_score"] = 0.01
                        chunk_copy["graph_expanded"] = True
                        chunk_copy["expanded_relation"] = f"callee (out) from {curr.split('::')[-1]} (depth {depth+1})"
                        expanded_chunks.append(chunk_copy)
                        seen_ids.add(succ)
                    relations_log.append(f"{curr.split('::')[-1]} --[calls]--> {succ.split('::')[-1]}")
                    queue.append((succ, depth + 1))
                    
            # 2. Predecessors (Callers)
            for pred in _GRAPH_DB.g.predecessors(curr):
                edge_data = _GRAPH_DB.g.get_edge_data(pred, curr)
                relation = edge_data.get("relation", "")
                if relation == "calls" and pred not in visited:
                    visited.add(pred)
                    neighbor_chunk = _CHUNKS_BY_ID.get(pred)
                    if neighbor_chunk:
                        chunk_copy = neighbor_chunk.copy()
                        chunk_copy["rrf_score"] = 0.01
                        chunk_copy["graph_expanded"] = True
                        chunk_copy["expanded_relation"] = f"caller (in) from {curr.split('::')[-1]} (depth {depth+1})"
                        expanded_chunks.append(chunk_copy)
                        seen_ids.add(pred)
                    relations_log.append(f"{pred.split('::')[-1]} --[calls]--> {curr.split('::')[-1]}")
                    queue.append((pred, depth + 1))
                    
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
    
    # 2. OVERVIEW query bypass
    if query_type == "OVERVIEW":
        overview_results = []
        # Check if the query specifies a particular repository
        target_repo = None
        q_lower = query.lower()
        for r in REPOSITORIES:
            # check if repo name (or first token of name) is in query
            repo_name_clean = r["name"].lower()
            name_token = repo_name_clean.split("-")[0] if "-" in repo_name_clean else repo_name_clean
            if repo_name_clean in q_lower or name_token in q_lower:
                target_repo = r["name"]
                break
                
        for cid, chunk in _CHUNKS_BY_ID.items():
            # If a specific repository was targeted, filter out chunks of other repos
            if target_repo and chunk.get("repo_name") != target_repo:
                continue
                
            if cid.startswith("repo_map::") or chunk.get("type") in {"DOC", "DOCS"} or "readme.md" in cid.lower():
                overview_results.append(chunk.copy())
                
        if overview_results:
            reranked = rerank_results(query, overview_results, top_k=top_k)
            return {
                "query": query,
                "query_type": "OVERVIEW",
                "results": reranked,
                "statistics": {
                    "vector_count": 0,
                    "bm25_count": 0,
                    "exact_count": 0,
                    "total_candidates": len(overview_results)
                }
            }
            
    # 3. Adjust candidate pools based on query classification
    vector_k = 20
    bm25_k = 20
    
    # 4. Retrieve standard candidates
    v_results = vector_search(query, top_k=vector_k)
    b_results = bm25_search(query, top_k=bm25_k)
    e_results = graph_exact_search(query)
    
    if query_type == "FILE_RECOVERY":
        file_results = graph_file_recovery_search(query)
        e_results.extend(file_results)
    
    # 5. RRF Rank Fusion
    fused = reciprocal_rank_fusion(v_results, b_results, e_results)
    
    # 6. Graph Neighbors Expansion
    if query_type == "DEBUG":
        expanded = expand_debug_graph(fused, max_seeds=5, max_neighbors=15)
    else:
        expanded = expand_retrieved_graph(fused, max_seeds=5, max_neighbors=15)
    
    # 7. CrossEncoder Reranking
    reranked = rerank_results(query, expanded, top_k=top_k)
    
    return {
        "query": query,
        "query_type": query_type,
        "results": reranked,
        "statistics": {
            "vector_count": len(v_results),
            "bm25_count": len(b_results),
            "exact_count": len(e_results),
            "total_candidates": len(expanded)
        }
    }