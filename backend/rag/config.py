# =========================================================
# V2 RAG CONFIGURATION
# =========================================================

import os

# Qdrant Database Settings
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "code_rag_v2"

def get_collection_name(repo_name: str) -> str:
    """Dynamically generates a clean, standard Qdrant collection name for a given repository."""
    safe_name = repo_name.lower().replace("-", "_").replace(" ", "_")
    return f"code_rag_v2_{safe_name}"


# Retrieval Settings
TOP_K = 10
RRF_K = 60  # RRF constant

# Model Settings
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
OLLAMA_MODEL = "qwen2.5-coder:7b"

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
        "path": os.path.join(BACKEND_DIR, "repositories", "face_validation", "face_validation"),
        "description": "Face validation system using RetinaFace, YOLO, and Camera stream validation."
    },
    {
        "name": "sboss-dashboard-deployment",
        "path": os.path.join(BACKEND_DIR, "repositories", "sboss-dashboard-deployment", "sboss-dashboard-deployment"),
        "description": "sboss-dashboard-deployment."
    },
    {
        "name": "BiometrikOnlineAttendance-master",
        "path": os.path.join(BACKEND_DIR, "repositories", "BiometrikOnlineAttendance-master", "BiometrikOnlineAttendance-master"),
        "description": "Biometrik Online Attendance Android/C++ App."
    },
    {
        "name": "CSC-Jharkhand-attendance-app-main",
        "path": os.path.join(BACKEND_DIR, "repositories", "CSC-Jharkhand-attendance-app-main", "CSC-Jharkhand-attendance-app-main"),
        "description": "CSC Jharkhand attendance React Native App."
    },
    {
        "name": "csc-jharkhand-deployment",
        "path": os.path.join(BACKEND_DIR, "repositories", "csc-jharkhand-deployment", "csc-jharkhand-deployment"),
        "description": "CSC Jharkhand deployment (Next.js Frontend & Express Backend)."
    },
    {
        "name": "pan_ocr-feature-dev",
        "path": os.path.join(BACKEND_DIR, "repositories", "pan_ocr-feature-dev", "pan_ocr-feature-dev"),
        "description": "PAN OCR feature development Python service."
    },
    {
        "name": "qrScannerPOC-test-cpp",
        "path": os.path.join(BACKEND_DIR, "repositories", "qrScannerPOC-test-cpp", "qrScannerPOC-test-cpp"),
        "description": "QR Scanner Proof of Concept React Native/C++ App."
    },
    {
        "name": "record-cctv-app-feature-dev",
        "path": os.path.join(BACKEND_DIR, "repositories", "record-cctv-app-feature-dev", "record-cctv-app-feature-dev"),
        "description": "CCTV Recording Qt/C++ Application."
    },
    {
        "name": "LivenessApp-tflite-main",
        "path": os.path.join(BACKEND_DIR, "repositories", "LivenessApp-tflite-main", "LivenessApp-tflite-main"),
        "description": "Biometric face liveness detection application using TensorFlow Lite."
    },
    {
        "name": "ndisl-fra-portal-deployment",
        "path": os.path.join(BACKEND_DIR, "repositories", "ndisl-fra-portal-deployment", "ndisl-fra-portal-deployment"),
        "description": "NDISL FRA Next.js deployment Portal."
    }
]