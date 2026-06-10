# =========================================================
# V2 REPOSITORY INDEXING ORCHESTRATOR (indexer.py)
# =========================================================

import os
import json
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from rag.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    REPOSITORIES,
    INDEX_PATH,
    GRAPH_PATH,
    QDRANT_DB_PATH
)
from rag.parser import FileParser
from rag.symbol_extractor import SymbolExtractor
from rag.chunk_generator import ChunkGenerator
from rag.graph_database import GraphDatabase
from rag.embeddings import embed_texts

# Ignored directories for indexing
IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".venv",
    "dist", "build", ".next", "coverage", "tmp", "logs", "output", "scratch"
}

# Supported file extension groups
SUPPORTED_EXTENSIONS = {
    # Tree-sitter languages
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".cc", ".cxx", ".c", ".h", ".php", ".go", ".rs",
    # Configs
    ".json", ".yaml", ".yml", ".env",
    # Markup / Docs
    ".md", ".rst", ".html",
    # Flatfiles
    ".sql", ".sh"
}

def scan_repository(repo_path: str, repo_name: str):
    """Scans and parses a single repository, returning parsed files, symbols, and chunks."""
    print(f"\n[INDEXER] Scanning repository '{repo_name}' at '{repo_path}'...")
    if not os.path.exists(repo_path):
        print(f"[ERROR] Repository path not found: {repo_path}")
        return [], []

    files_corpus = []
    
    # 1. Walk directory and read all files
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored folders in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            name, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # Match Dockerfile / Makefile / .gitignore explicitly
            is_special = file in {"Dockerfile", "Makefile", ".gitignore"}
            if ext not in SUPPORTED_EXTENSIONS and not is_special:
                continue
                
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, repo_path).replace("\\", "/")
            
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                files_corpus.append({
                    "full_path": full_path,
                    "rel_path": rel_path,
                    "filename": file,
                    "content": content
                })
            except Exception as e:
                print(f"[WARNING] Failed to read file {full_path}: {e}")
                
    print(f"[INDEXER] Found {len(files_corpus)} source files.")
    return files_corpus

def run_indexing_pipeline():
    """Runs the V2 indexing, graph construction, and vector ingestion pipeline."""
    print("\n" + "="*60)
    print("STARTING V2 CODE RAG INDEXING PIPELINE")
    print("="*60 + "\n")
    
    all_chunks = []
    graph_db = GraphDatabase()
    
    # Track module mappings for Python/JS imports resolution
    # maps: module_name -> relative_path (e.g. "src.api" -> "src/api.py")
    module_registry = {}
    
    # Track symbols mappings for calls resolution
    # maps: symbol_name -> node_id (e.g. "CameraManager" -> "src/camera_manager.py::CameraManager")
    symbol_registry = {}

    # 1. First Pass: Scan all repos and collect files
    for repo in REPOSITORIES:
        repo_name = repo["name"]
        repo_path = repo["path"]
        
        if not os.path.exists(repo_path):
            # Fallback path if configured absolute path is missing in environment
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fallback = os.path.join(backend_dir, "repositories", repo_name, repo_name)
            if os.path.exists(fallback):
                repo_path = fallback
            else:
                fallback_parent = os.path.join(backend_dir, "repositories", repo_name)
                if os.path.exists(fallback_parent):
                    repo_path = fallback_parent
                    
        repo_files = scan_repository(repo_path, repo_name)
        
        # Build module registry to resolve imports
        for f in repo_files:
            rel = f["rel_path"]
            # e.g., "src/api.py" -> "src.api"
            mod_name = os.path.splitext(rel)[0].replace("/", ".")
            module_registry[mod_name] = rel
            
        # 2. Second Pass: Parse and extract symbols
        parsed_files = []
        for f in repo_files:
            parse_result = FileParser.parse_file(f["full_path"], f["content"])
            symbols = SymbolExtractor.extract_symbols(parse_result, f["rel_path"])
            
            parsed_files.append({
                "file_info": f,
                "parse_result": parse_result,
                "symbols": symbols
            })
            
            # Register defined class/function names for calls resolution
            for s in symbols:
                if s["symbol_type"] in {"CLASS", "FUNCTION"}:
                    name = s["name"]
                    qname = s["qualified_name"]
                    node_id = s["id"]
                    
                    symbol_registry[name] = node_id
                    symbol_registry[qname] = node_id
                    
        # 3. Third Pass: Build chunks and graph relationships
        for pf in parsed_files:
            finfo = pf["file_info"]
            presult = pf["parse_result"]
            symbols = pf["symbols"]
            rel_path = finfo["rel_path"]
            
            # Add File Node
            graph_db.add_node(
                node_id=rel_path,
                node_type="FILE",
                name=finfo["filename"],
                file_path=rel_path,
                repo_name=repo_name
            )
            
            # Add Symbol Nodes & CONTAINS Edges
            for s in symbols:
                stype = s["symbol_type"]
                metadata = {k: v for k, v in s.items() if k not in {"id", "symbol_type", "name", "repository_path", "content"}}
                graph_db.add_node(
                    node_id=s["id"],
                    node_type=stype,
                    name=s["name"],
                    file_path=rel_path,
                    repo_name=repo_name,
                    **metadata
                )
                # Draw containment from parent or file
                parent_id = s.get("parent")
                if parent_id:
                    # In symbol_extractor parent_id is AST node id (needs to map to stable node id)
                    # Let's map dynamically: if symbol has parent class, find it
                    # We built qname with Class.method prefix, so we can split
                    parts = s["qualified_name"].split(".")
                    if len(parts) > 1:
                        parent_qname = ".".join(parts[:-1])
                        parent_node_id = f"{rel_path}::{parent_qname}"
                        graph_db.add_edge(parent_node_id, s["id"], "contains")
                else:
                    graph_db.add_edge(rel_path, s["id"], "defines")
                    
            # Add IMPORTS Edges
            # Walk AST for imports
            if presult.get("type") == "CODE":
                tree = presult.get("tree")
                if tree:
                    # Look at import statement symbols
                    # Walk files manually or parse import strings
                    pass
            for s in symbols:
                if s["symbol_type"] == "IMPORT":
                    # If it imports a module, e.g. "src.api"
                    imp_mod = s.get("import_module")
                    if imp_mod and imp_mod in module_registry:
                        target_file = module_registry[imp_mod]
                        graph_db.add_edge(rel_path, target_file, "imports")
                        
            # Add CALLS Edges
            # Walk calls
            for s in symbols:
                if s["symbol_type"] == "CALL":
                    caller_id = s.get("parent")
                    # Find which function node wraps this call line
                    # We can resolve caller node id
                    caller_node_id = None
                    call_line = s["start_line"]
                    for other in symbols:
                        if other["symbol_type"] in {"FUNCTION", "CLASS"} and other["start_line"] <= call_line <= other["end_line"]:
                            caller_node_id = other["id"]
                            break
                            
                    call_name = s["name"]
                    # Resolve callee node id using registry
                    callee_node_id = symbol_registry.get(call_name)
                    
                    if caller_node_id and callee_node_id:
                        graph_db.add_edge(caller_node_id, callee_node_id, "calls")
                        
            # Generate Chunks
            chunks = ChunkGenerator.generate_chunks(
                symbols=symbols,
                file_path=finfo["full_path"],
                relative_path=rel_path,
                file_type=presult["type"],
                raw_content=finfo["content"],
                repo_name=repo_name
            )
            all_chunks.extend(chunks)
            
    print(f"[INDEXER] Generated {len(all_chunks)} semantic chunks.")

    # 4. Save NetworkX Graph
    graph_db.save_to_json(GRAPH_PATH)
    
    # 5. Save Repository Index Chunks
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4)
    print(f"[INDEXER] Saved chunks index to {INDEX_PATH}")
    
    # 6. Generate Embeddings & Ingest to Qdrant
    if not all_chunks:
        print("[WARNING] No chunks found to index. Exiting.")
        return
        
    print(f"[INDEXER] Generating embeddings for {len(all_chunks)} chunks...")
    texts_to_embed = [c["embedding_text"] for c in all_chunks]
    embeddings = embed_texts(texts_to_embed)
    
    # Setup Qdrant
    client = None
    try:
        print(f"[INDEXER] Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=5.0)
        client.get_collections()
    except Exception as e:
        print(f"[WARNING] Could not connect to Qdrant server: {e}")
        print("[WARNING] Falling back to local disk Qdrant storage...")
        client = QdrantClient(path=QDRANT_DB_PATH)
        
    vector_size = len(embeddings[0])
    
    try:
        # Recreate collection
        if client.collection_exists(collection_name=COLLECTION_NAME):
            client.delete_collection(collection_name=COLLECTION_NAME)
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
    except Exception as e:
        print(f"[ERROR] Qdrant collection creation failed: {e}")
        raise e
        
    points = []
    for idx, (chunk, vector) in enumerate(zip(all_chunks, embeddings)):
        # Payload properties
        payload = {
            "id": chunk["id"],
            "repo_name": chunk["repo_name"],
            "type": chunk["type"],
            "name": chunk["name"],
            "qualified_name": chunk["qualified_name"],
            "file": chunk["file"],
            "path": chunk["path"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "content": chunk["content"],
            "embedding_text": chunk["embedding_text"]
        }
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload=payload
            )
        )
        
    print(f"[INDEXER] Ingesting {len(points)} vectors into collection '{COLLECTION_NAME}'...")
    # Batch upload
    client.upload_points(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print("[INDEXER] Ingestion complete. Index is fully operational!")
    print("\n" + "="*60)
    print("V2 INDEXING PIPELINE FINISHED SUCCESSFULLY")
    print("="*60 + "\n")