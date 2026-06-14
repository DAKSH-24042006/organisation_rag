import os
import sys
from pathlib import Path

# Add backend dir to path to ensure imports work
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.append(str(BACKEND_DIR))

from rag.retriever import retrieve, _ensure_initialized, _CHUNKS_BY_ID, _GRAPH_DB
from rag.analysis import RepositoryAnalyzer

def search_codebase(query: str, top_k: int = 5) -> list[dict]:
    """
    Search the codebase using hybrid dense-sparse vector search.
    Returns a list of matching code chunks.
    """
    try:
        retrieval_data = retrieve(query, top_k=top_k)
        results = retrieval_data.get("results", [])
        return [{
            "id": r.get("id"),
            "path": r.get("path"),
            "name": r.get("name"),
            "type": r.get("type"),
            "start_line": r.get("start_line"),
            "end_line": r.get("end_line"),
            "content": r.get("content")
        } for r in results]
    except Exception as e:
        print(f"[Agent Tools ERROR] search_codebase failed: {e}")
        return []

def find_dependencies(file_path: str) -> list[str]:
    """
    Find files imported by the given file (outgoing imports).
    """
    _ensure_initialized()
    if not _GRAPH_DB or file_path not in _GRAPH_DB.g:
        return []
    
    deps = []
    # Check successors of file_path
    for succ in _GRAPH_DB.g.successors(file_path):
        edge_data = _GRAPH_DB.g.get_edge_data(file_path, succ)
        if edge_data.get("relation") == "imports":
            deps.append(succ)
    return sorted(deps)

def find_callers(symbol_name: str) -> list[str]:
    """
    Find functions or classes calling the given symbol.
    """
    _ensure_initialized()
    if not _GRAPH_DB:
        return []
        
    callers = []
    symbol_node_id = None
    
    # Try direct mapping or suffix mapping
    for node_id in _GRAPH_DB.g.nodes:
        if symbol_name == node_id or node_id.endswith(f"::{symbol_name}"):
            symbol_node_id = node_id
            break
            
    if symbol_node_id:
        for pred in _GRAPH_DB.g.predecessors(symbol_node_id):
            edge_data = _GRAPH_DB.g.get_edge_data(pred, symbol_node_id)
            if edge_data.get("relation") == "calls":
                callers.append(pred)
                
    return sorted(callers)

def get_repo_summary() -> dict:
    """
    Get a high-level statistics and components summary of the repository.
    """
    try:
        analysis = RepositoryAnalyzer.analyze_repository()
        return {
            "statistics": analysis.get("statistics", {}),
            "major_components": list(analysis.get("components", {}).keys()),
            "api_endpoints": [f"{e['method']} {e['route']}" for e in analysis.get("endpoints_list", [])],
            "database_tables": [t["name"] for t in analysis.get("tables_list", [])]
        }
    except Exception as e:
        print(f"[Agent Tools ERROR] get_repo_summary failed: {e}")
        return {}

def analyse_impact(file_path: str) -> list[str]:
    """
    Trace what files/modules will be impacted if the given file is modified.
    """
    _ensure_initialized()
    if not _GRAPH_DB:
        return []
    return _GRAPH_DB.impact_analysis(file_path)
