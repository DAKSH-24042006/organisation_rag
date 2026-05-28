import os
import re
import json

from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

from rag.parser import (

    extract_functions,
    extract_classes,
    extract_imports,
    extract_dependencies,
    extract_react_components
)

from rag.embeddings import embedding_model

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

    ".java": "java"
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
# IGNORED FILES
# =========================================================

IGNORED_FILES = [

    ".min.js",
    ".bundle.js"
]

# =========================================================
# STORAGE
# =========================================================

code_chunks = []

# =========================================================
# QDRANT CLIENT
# =========================================================

client = QdrantClient(

    host=QDRANT_HOST,

    port=QDRANT_PORT
)

# =========================================================
# CREATE COLLECTION
# =========================================================

client.recreate_collection(

    collection_name=COLLECTION_NAME,

    vectors_config=VectorParams(

        size=384,

        distance=Distance.COSINE
    )
)

print("\nQdrant collection ready.\n")

# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = re.sub(

        r"\n{2,}",

        "\n",

        text
    )

    return text.strip()

# =========================================================
# CREATE CHUNK
# =========================================================

def create_chunk(

    repo_metadata,
    language,
    chunk_type,
    name,
    file_path,
    content,
    imports=None,
    dependencies=None,
    parent_class=None,
    docstring=""

):

    if imports is None:
        imports = []

    if dependencies is None:
        dependencies = []

    chunk = {

        "repo_name":
        repo_metadata["name"],

        "team":
        repo_metadata["team"],

        "framework":
        repo_metadata["framework"],

        "architecture":
        repo_metadata["architecture"],

        "language":
        language,

        "type":
        chunk_type,

        "name":
        name,

        "file":
        os.path.basename(file_path),

        "path":
        file_path,

        "imports":
        imports,

        "dependencies":
        dependencies,

        "parent_class":
        parent_class,

        "docstring":
        docstring,

        "content":
        clean_text(content)
    }

    code_chunks.append(chunk)

# =========================================================
# PROCESS CODE FILE
# =========================================================

def process_code_file(

    file_path,
    repo_metadata

):

    try:

        extension = os.path.splitext(
            file_path
        )[1]

        # =================================================
        # SKIP UNSUPPORTED FILES
        # =================================================

        if extension not in SUPPORTED_EXTENSIONS:
            return

        # =================================================
        # SKIP IGNORED FILES
        # =================================================

        if any(

            ignored in file_path

            for ignored in IGNORED_FILES
        ):

            return

        language = SUPPORTED_EXTENSIONS[
            extension
        ]

        with open(

            file_path,

            "r",

            encoding="utf-8",

            errors="ignore"

        ) as f:

            source_code = f.read()

        source_code = clean_text(
            source_code
        )

        # =================================================
        # IMPORTS
        # =================================================

        imports = extract_imports(

            source_code,
            extension
        )

        # =================================================
        # DEPENDENCIES
        # =================================================

        dependencies = extract_dependencies(

            source_code,
            extension
        )

        # =================================================
        # REACT COMPONENTS
        # =================================================

        react_components = extract_react_components(

            source_code,
            extension
        )

        for component in react_components:

            create_chunk(

                repo_metadata=repo_metadata,

                language=language,

                chunk_type="react_component",

                name=component["name"],

                file_path=file_path,

                content=component["content"],

                imports=imports,

                dependencies=dependencies
            )

        # =================================================
        # FUNCTIONS
        # =================================================

        functions = extract_functions(

            source_code,
            extension
        )

        for func in functions:

            semantic_type = "function"

            function_name = func["name"].lower()

            # =============================================
            # ARCHITECTURE DETECTION
            # =============================================

            if "api" in function_name:

                semantic_type = "api_service"

            elif "hook" in function_name:

                semantic_type = "react_hook"

            elif "route" in function_name:

                semantic_type = "route_handler"

            elif "auth" in function_name:

                semantic_type = "auth_service"

            elif "dashboard" in function_name:

                semantic_type = "dashboard_component"

            create_chunk(

                repo_metadata=repo_metadata,

                language=language,

                chunk_type=semantic_type,

                name=func["name"],

                file_path=file_path,

                content=func["content"],

                imports=imports,

                dependencies=dependencies
            )

        # =================================================
        # CLASSES
        # =================================================

        classes = extract_classes(

            source_code,
            extension
        )

        for cls in classes:

            create_chunk(

                repo_metadata=repo_metadata,

                language=language,

                chunk_type="class",

                name=cls["name"],

                file_path=file_path,

                content=cls["content"],

                imports=imports,

                dependencies=dependencies
            )

        # =================================================
        # FILE CHUNK ONLY AS FALLBACK
        # =================================================

        if (

            len(functions) == 0
            and
            len(classes) == 0
            and
            len(react_components) == 0
        ):

            create_chunk(

                repo_metadata=repo_metadata,

                language=language,

                chunk_type="file",

                name=os.path.basename(
                    file_path
                ),

                file_path=file_path,

                content=source_code[:3000],

                imports=imports,

                dependencies=dependencies
            )

        print(
            f"[INFO] Processed: {file_path}"
        )

    except Exception as e:

        print(
            f"[ERROR] {file_path}: {e}"
        )

# =========================================================
# INDEX REPOSITORIES
# =========================================================

def index_repositories():

    print("\nScanning repositories...\n")

    for repo in REPOSITORIES:

        repo_path = repo["path"]

        print(
            f"\nIndexing: {repo['name']}\n"
        )

        for root, dirs, files in os.walk(
            repo_path
        ):

            # =============================================
            # FILTER DIRECTORIES
            # =============================================

            dirs[:] = [

                d for d in dirs

                if d not in IGNORED_DIRECTORIES
            ]

            for file in files:

                if (

                    file.endswith((

                        ".py",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".java"

                    ))

                    and

                    not any(

                        ignored in file

                        for ignored in IGNORED_FILES
                    )
                ):

                    file_path = os.path.join(
                        root,
                        file
                    )

                    process_code_file(

                        file_path,
                        repo
                    )

    print("\n" + "=" * 60)

    print("REPOSITORIES INDEXED")

    print("=" * 60)

    print(
        f"\nTotal Chunks: "
        f"{len(code_chunks)}"
    )

# =========================================================
# BUILD DOCUMENTS
# =========================================================

def build_documents():

    documents = []

    bm25_corpus = []

    for chunk in code_chunks:

        document = f'''

Repository:
{chunk['repo_name']}

Team:
{chunk['team']}

Framework:
{chunk['framework']}

Architecture:
{chunk['architecture']}

Language:
{chunk['language']}

Type:
{chunk['type']}

Name:
{chunk['name']}

Imports:
{" ".join(chunk['imports'])}

Dependencies:
{" ".join(chunk['dependencies'])}

Docstring:
{chunk['docstring']}

Code:
{chunk['content']}
'''

        documents.append(document)

        tokens = document.lower().split()

        bm25_corpus.append(tokens)

    return documents, bm25_corpus

# =========================================================
# GENERATE EMBEDDINGS
# =========================================================

def generate_embeddings(documents):

    print("\nGenerating embeddings...\n")

    embeddings = embedding_model.encode(

        documents,

        show_progress_bar=True
    )

    return embeddings

# =========================================================
# STORE VECTORS
# =========================================================

def store_vectors(embeddings):

    print("\nUploading vectors...\n")

    if len(code_chunks) == 0:

        raise ValueError(
            "No chunks found. "
            "Check repository paths."
        )

    points = []

    for idx, (

        chunk,
        embedding

    ) in enumerate(

        zip(code_chunks, embeddings)

    ):

        point = PointStruct(

            id=idx,

            vector=embedding.tolist(),

            payload=chunk
        )

        points.append(point)

    client.upsert(

        collection_name=COLLECTION_NAME,

        points=points
    )

    print("\nVectors uploaded.")

# =========================================================
# SAVE METADATA
# =========================================================

def save_metadata():

    os.makedirs(

        "data",

        exist_ok=True
    )

    with open(

        "data/repository_index.json",

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            code_chunks,

            f,

            indent=2
        )

    print("\nMetadata saved.")