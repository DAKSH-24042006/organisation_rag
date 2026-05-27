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

        "path": r"C:\xampp\htdocs\employee_system"
    }
]

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)