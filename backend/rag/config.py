QDRANT_HOST = "localhost"

QDRANT_PORT = 6333

COLLECTION_NAME = "enterprise_repo"

TOP_K = 5

REPOSITORIES = [

    {
        "name": "enterprise_repo",

        "team": "backend",

        "framework": "FastAPI",

        "architecture": "microservices",

        "path": r"D:\orgatisation_rag\backend\repositories"
    }
]

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

# =========================================================
# OLLAMA MODEL
# =========================================================

OLLAMA_MODEL = "deepseek-coder:6.7b"