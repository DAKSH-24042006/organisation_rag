# =========================================================
# V2 RAG CONFIGURATION
# =========================================================

import os

# Qdrant Database Settings
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "code_rag_v2"

# Retrieval Settings
TOP_K = 10
RRF_K = 60  # RRF constant

# Model Settings
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"

# Repository Roots to Index
# We point to the main project directory in repositories
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPO_PATH = r"C:\Users\daksh\Downloads\face_validation (1)\face_validation"

# Storage Paths (Consolidated inside backend/data)
DATA_DIR = os.path.join(BACKEND_DIR, "data")
INDEX_PATH = os.path.join(DATA_DIR, "repository_index.json")
GRAPH_PATH = os.path.join(DATA_DIR, "repository_graph.json")
QDRANT_DB_PATH = os.path.join(DATA_DIR, "qdrant_db")

REPOSITORIES = [
    {
        "name": "face_validation",
        "path": r"C:\Users\daksh\Downloads\face_validation (1)\face_validation",
        "description": "Face validation system using RetinaFace, YOLO, and Camera stream validation."
    }
]