# =========================================================
# STANDARD LIBRARIES
# =========================================================

import os
import json

# =========================================================
# QDRANT
# =========================================================

from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

# =========================================================
# PARSER
# =========================================================

from rag.parser import (
    get_repository_symbols
)

# =========================================================
# CHUNK GENERATOR
# =========================================================

from rag.chunk_generator import (
    generate_chunks
)

# =========================================================
# EMBEDDINGS
# =========================================================

from rag.embeddings import (
    embedding_model
)

# =========================================================
# CONFIG
# =========================================================

from rag.config import (

    QDRANT_HOST,

    QDRANT_PORT,

    COLLECTION_NAME,

    REPOSITORIES
)

# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

SUPPORTED_EXTENSIONS = {

    ".py": "python",

    ".js": "javascript",

    ".jsx": "javascript",

    ".ts": "typescript",

    ".tsx": "typescript",

    ".java": "java",

    ".php": "php",

    ".go": "go",

    ".rs": "rust",

    ".c": "c",

    ".cpp": "cpp",

    ".cc": "cpp",

    ".cxx": "cpp",

    ".cs": "c_sharp",

    ".rb": "ruby",

    ".kt": "kotlin",

    ".swift": "swift",

    ".scala": "scala",

    ".lua": "lua",

    ".sh": "bash"
}

# =========================================================
# IGNORED DIRECTORIES
# =========================================================

IGNORED_DIRECTORIES = [

    "node_modules",

    ".git",

    "__pycache__",

    "venv",

    ".venv",

    "dist",

    "build",

    ".next",

    "coverage",

    ".idea",

    ".vscode",

    "target",

    "bin",

    "obj",

    "out",

    "vendor",

    "tmp",

    "logs"
]

# =========================================================
# GLOBAL STORAGE
# =========================================================

code_chunks = []

# =========================================================
# VECTOR SIZE
# =========================================================

VECTOR_SIZE = len(

    embedding_model.encode(

        ["test"]

    )[0]
)

# =========================================================
# QDRANT CLIENT WITH FALLBACK
# =========================================================

try:
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        timeout=5.0
    )
    # Check connection
    client.get_collections()
    print("Successfully connected to Qdrant server.")
except Exception as e:
    print(f"\n[WARNING] Could not connect to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}: {e}")
    print("Falling back to local disk-based Qdrant client at 'data/qdrant_db'...\n")
    client = QdrantClient(path="data/qdrant_db")

# =========================================================
# COLLECTION
# =========================================================

try:
    if client.collection_exists(collection_name=COLLECTION_NAME):
        client.delete_collection(collection_name=COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
except Exception as e:
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
    except Exception as inner_e:
        print(f"[ERROR] Failed to recreate collection: {inner_e}")
        raise inner_e

print(
    "\nQdrant collection ready.\n"
)

# =========================================================
# DETECT LANGUAGE
# =========================================================

def detect_language(file_path):

    _, extension = os.path.splitext(
        file_path
    )

    return SUPPORTED_EXTENSIONS.get(
        extension.lower()
    )

# =========================================================
# READ FILE
# =========================================================

def read_source_file(file_path):

    try:

        with open(

            file_path,

            "r",

            encoding="utf-8",

            errors="ignore"

        ) as f:

            return f.read()

    except Exception as e:

        print(
            f"[ERROR] Failed reading {file_path}: {e}"
        )

        return None





# =========================================================
# BUILD EMBEDDING TEXT
# =========================================================

def build_embedding_text(chunk):

    imports = chunk.get(
        "imports",
        []
    )

    calls = chunk.get(
        "calls",
        []
    )

    imports_text = " ".join(
        imports
    )

    calls_text = " ".join(
        calls
    )

    decorators_text = " ".join(
        chunk.get(
            "decorators",
            []
        )
    )

    hooks_text = " ".join(
        chunk.get(
            "hooks",
            []
        )
    )

    return f"""

Repository:
{chunk.get('repo_name','')}

Language:
{chunk.get('language','')}

Chunk Type:
{chunk.get('type','')}

Name:
{chunk.get('name','')}

Framework:
{chunk.get('framework','')}

Component Type:
{chunk.get('component_type','')}

Service Type:
{chunk.get('service_type','')}

Route:
{chunk.get('route','')}

HTTP Method:
{chunk.get('http_method','')}

Namespace:
{chunk.get('namespace','')}

Async:
{chunk.get('is_async', False)}

Decorators:
{decorators_text}

Hooks:
{hooks_text}

Imports:
{imports_text}

Calls:
{calls_text}

Workflow Relationships:
{calls_text}

Code:
{chunk.get('content','')}
"""

# =========================================================
# PROCESS FILE
# =========================================================

def process_code_file(

    file_path,

    repo_name

):

    source_code = read_source_file(
        file_path
    )

    if not source_code:

        return

    language = detect_language(
        file_path
    )

    if language is None:

        return

    _, extension = os.path.splitext(
        file_path
    )

    try:

        # =====================================
        # TREE SITTER
        # =====================================

        symbols = get_repository_symbols(

            source_code,

            extension
        )

        # =====================================
        # CHUNK GENERATOR
        # =====================================

        chunks = generate_chunks(

            symbols=symbols,

            source_code=source_code,

            language=language,

            file_path=file_path,

            repo_name=repo_name
        )

        # =====================================
        # ENRICH CHUNKS
        # =====================================

        imports = [

            x.get("name", "")

            for x in symbols.get(
                "imports",
                []
            )
        ]

        calls = [

            x.get("name", "")

            for x in symbols.get(
                "calls",
                []
            )
        ]

        for chunk in chunks:

            chunk["imports"] = imports

            chunk["calls"] = calls

            chunk[
                "embedding_text"
            ] = build_embedding_text(
                chunk
            )

            code_chunks.append(
                chunk
            )

        print(

            f"[OK] "

            f"{language:<12}"

            f"{len(chunks):>4} chunks "

            f"{file_path}"
        )

    except Exception as e:

        print(

            f"[ERROR] "

            f"{file_path}: "

            f"{e}"
        )


# =========================================================
# REPOSITORY SCANNER
# =========================================================

def scan_repository(

    repo_path,

    repo_name

):

    print(
        f"\nIndexing: {repo_name}\n"
    )

    file_count = 0

    for root, dirs, files in os.walk(
        repo_path
    ):

        # =====================================
        # SKIP USELESS DIRECTORIES
        # =====================================

        dirs[:] = [

            d

            for d in dirs

            if d not in IGNORED_DIRECTORIES
        ]

        for file_name in files:

            _, extension = os.path.splitext(
                file_name
            )

            if (

                extension.lower()

                not in

                SUPPORTED_EXTENSIONS

            ):

                continue

            file_path = os.path.join(

                root,

                file_name
            )

            process_code_file(

                file_path,

                repo_name
            )

            file_count += 1

    print(
        f"\nProcessed {file_count} files\n"
    )

# =========================================================
# SCAN ALL REPOSITORIES
# =========================================================

def scan_all_repositories():

    print(
        "\nScanning repositories...\n"
    )

    for repo in REPOSITORIES:

        repo_name = repo.get(
            "name",
            "unknown_repo"
        )

        repo_path = repo.get(
            "path"
        )

        if not repo_path:

            continue

        if not os.path.exists(
            repo_path
        ):
            # Check fallback path in workspace repositories directory
            local_fallback = os.path.join(os.path.dirname(os.path.dirname(__file__)), "repositories", repo_name)
            if os.path.exists(local_fallback):
                print(f"[INFO] Configured path '{repo_path}' not found. Falling back to local workspace directory: '{local_fallback}'")
                repo_path = local_fallback
            else:
                print(

                    f"[WARNING] "

                    f"Repository not found: "

                    f"{repo_path}"
                )

                continue

        scan_repository(

            repo_path,

            repo_name
        )

# =========================================================
# CHUNK STATISTICS
# =========================================================

def print_statistics():

    print("\n")

    print("=" * 60)

    print(
        "REPOSITORIES INDEXED"
    )

    print("=" * 60)

    print(
        f"\nTotal Chunks: "
        f"{len(code_chunks)}"
    )

    chunk_types = {}

    languages = {}

    for chunk in code_chunks:

        chunk_type = chunk.get(
            "type",
            "UNKNOWN"
        )

        language = chunk.get(
            "language",
            "UNKNOWN"
        )

        chunk_types[
            chunk_type
        ] = (

            chunk_types.get(
                chunk_type,
                0
            )
            + 1
        )

        languages[
            language
        ] = (

            languages.get(
                language,
                0
            )
            + 1
        )

    print(
        "\nChunk Types:"
    )

    for key, value in sorted(

        chunk_types.items()

    ):

        print(
            f"  {key:<20} {value}"
        )

    print(
        "\nLanguages:"
    )

    for key, value in sorted(

        languages.items()

    ):

        print(
            f"  {key:<20} {value}"
        )


# =========================================================
def generate_embeddings():
    print("\nGenerating embeddings...\n")
    if len(code_chunks) == 0:
        raise ValueError("No chunks generated.")
    # Limit each embedding text to a maximum number of characters to avoid token overflow
    MAX_CHARS = 2000
    texts = [chunk["embedding_text"][:MAX_CHARS] for chunk in code_chunks]
    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    return embeddings
# =========================================================

def store_vectors(embeddings):

    print(
        "\nUploading vectors...\n"
    )

    points = []

    for idx, (

        chunk,
        vector

    ) in enumerate(

        zip(
            code_chunks,
            embeddings
        )
    ):

        payload = {

    "repo_name":
    chunk["repo_name"],

    "language":
    chunk["language"],

    "type":
    chunk["type"],

    "name":
    chunk["name"],

    "file":
    chunk["file"],

    "path":
    chunk["path"],

    "start_line":
    chunk["start_line"],

    "end_line":
    chunk["end_line"],

    # ====================================
    # FRAMEWORK METADATA
    # ====================================

    "framework":
    chunk.get(
        "framework"
    ),

    "component_type":
    chunk.get(
        "component_type"
    ),

    "service_type":
    chunk.get(
        "service_type"
    ),

    "route":
    chunk.get(
        "route"
    ),

    "http_method":
    chunk.get(
        "http_method"
    ),

    "decorators":
    chunk.get(
        "decorators",
        []
    ),

    "annotations":
    chunk.get(
        "annotations",
        []
    ),

    "hooks":
    chunk.get(
        "hooks",
        []
    ),

    "namespace":
    chunk.get(
        "namespace"
    ),

    "includes":
    chunk.get(
        "includes",
        []
    ),

    "stl_usage":
    chunk.get(
        "stl_usage",
        []
    ),

    "is_async":
    chunk.get(
        "is_async",
        False
    ),

    # ====================================
    # EXISTING METADATA
    # ====================================

    "imports":
    chunk.get(
        "imports",
        []
    ),

    "calls":
    chunk.get(
        "calls",
        []
    ),

    "content":
    chunk["content"]
}

        points.append(

            PointStruct(

                id=idx,

                vector=vector.tolist(),

                payload=payload
            )
        )

    BATCH_SIZE = 100

    for i in range(

        0,

        len(points),

        BATCH_SIZE
    ):

        batch = points[
            i:
            i + BATCH_SIZE
        ]

        client.upsert(

            collection_name=
            COLLECTION_NAME,

            points=batch
        )

    print(
        "\nVectors uploaded.\n"
    )

# =========================================================
# SAVE CHUNKS
# =========================================================

def save_repository_index():

    print(
        "\nSaving metadata...\n"
    )

    os.makedirs(
        "data",
        exist_ok=True
    )

    save_chunks = []

    for chunk in code_chunks:

        save_chunk = dict(
            chunk
        )

        if (
            "embedding_text"
            in
            save_chunk
        ):

            del save_chunk[
                "embedding_text"
            ]

        save_chunks.append(
            save_chunk
        )

    with open(

        "data/repository_index.json",

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            save_chunks,

            f,

            indent=2,

            ensure_ascii=False
        )

    print(
        "\nMetadata saved.\n"
    )

# =========================================================
# SAVE SUMMARY
# =========================================================

def save_statistics():

    stats = {

        "total_chunks":
        len(code_chunks),

        "languages": {},

        "chunk_types": {}
    }

    for chunk in code_chunks:

        language = chunk[
            "language"
        ]

        chunk_type = chunk[
            "type"
        ]

        stats[
            "languages"
        ][language] = (

            stats[
                "languages"
            ].get(
                language,
                0
            )
            + 1
        )

        stats[
            "chunk_types"
        ][chunk_type] = (

            stats[
                "chunk_types"
            ].get(
                chunk_type,
                0
            )
            + 1
        )

    with open(

        "data/index_stats.json",

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            stats,

            f,

            indent=2
        )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print(
        "\nStarting Organization RAG indexing...\n"
    )

    # ==========================================
    # SCAN REPOSITORIES
    # ==========================================

    scan_all_repositories()

    # ==========================================
    # STATS
    # ==========================================

    print_statistics()

    # ==========================================
    # EMBEDDINGS
    # ==========================================

    embeddings = generate_embeddings()

    # ==========================================
    # QDRANT
    # ==========================================

    store_vectors(
        embeddings
    )

    # ==========================================
    # SAVE METADATA
    # ==========================================

    save_repository_index()

    save_statistics()

    print(
        "\nINDEXING COMPLETE\n"
    )