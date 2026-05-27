# =========================================================
# QDRANT CONFIG
# =========================================================

QDRANT_HOST = "localhost"

QDRANT_PORT = 6333

COLLECTION_NAME = "enterprise_rag"

# =========================================================
# RETRIEVAL CONFIG
# =========================================================

TOP_K = 5

# =========================================================
# LLM CONFIG
# =========================================================

OLLAMA_MODEL = "qwen2.5-coder:7b"

# =========================================================
# EMBEDDING MODEL
# =========================================================

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

# =========================================================
# MULTI REPOSITORY SUPPORT
# =========================================================

REPOSITORIES = [

    {
        "name": "oops_python",

        "path":
        r"C:\Users\daksh\OneDrive\Desktop\OOPS_PYTHON",

        "team": "backend",

        "framework": "python",

        "architecture": "layered"
    }

]