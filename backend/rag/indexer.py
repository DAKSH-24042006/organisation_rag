import os
import ast
import re
import json

from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

from rag.embeddings import embedding_model

from rag.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    REPOSITORIES
)

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

print("Qdrant collection ready.\n")

# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()

# =========================================================
# EXTRACT IMPORTS
# =========================================================

def extract_python_imports(tree):

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                imports.append(node.module)

    return list(set(imports))

# =========================================================
# EXTRACT DEPENDENCIES
# =========================================================

def extract_dependencies(node):

    dependencies = []

    for child in ast.walk(node):

        if isinstance(child, ast.Call):

            if isinstance(child.func, ast.Name):
                dependencies.append(child.func.id)

            elif isinstance(child.func, ast.Attribute):
                dependencies.append(child.func.attr)

    return list(set(dependencies))

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
# PROCESS PYTHON FILE
# =========================================================

def process_python_file(
    file_path,
    repo_metadata
):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        source_code = f.read()

    source_code = clean_text(source_code)

    try:

        tree = ast.parse(source_code)

    except Exception as e:

        print(f"AST Error in {file_path}: {e}")

        return

    imports = extract_python_imports(tree)

    # =====================================================
    # FILE CHUNK
    # =====================================================

    create_chunk(

        repo_metadata=repo_metadata,

        language="python",

        chunk_type="file",

        name=os.path.basename(file_path),

        file_path=file_path,

        content=source_code[:3000],

        imports=imports,

        docstring=ast.get_docstring(tree)
    )

    # =====================================================
    # AST WALK
    # =====================================================

    for node in ast.walk(tree):

        # -------------------------------------------------
        # CLASS CHUNKS
        # -------------------------------------------------

        if isinstance(node, ast.ClassDef):

            class_code = ast.get_source_segment(
                source_code,
                node
            )

            dependencies = extract_dependencies(node)

            create_chunk(

                repo_metadata=repo_metadata,

                language="python",

                chunk_type="class",

                name=node.name,

                file_path=file_path,

                content=class_code,

                imports=imports,

                dependencies=dependencies,

                docstring=ast.get_docstring(node)
            )

            # ---------------------------------------------
            # METHOD CHUNKS
            # ---------------------------------------------

            for child in node.body:

                if isinstance(
                    child,
                    ast.FunctionDef
                ):

                    method_code = (
                        ast.get_source_segment(
                            source_code,
                            child
                        )
                    )

                    method_dependencies = (
                        extract_dependencies(
                            child
                        )
                    )

                    create_chunk(

                        repo_metadata=
                        repo_metadata,

                        language="python",

                        chunk_type="method",

                        name=child.name,

                        file_path=file_path,

                        content=method_code,

                        imports=imports,

                        dependencies=
                        method_dependencies,

                        parent_class=node.name,

                        docstring=
                        ast.get_docstring(child)
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

            for file in files:

                if file.endswith(".py"):

                    file_path = os.path.join(
                        root,
                        file
                    )

                    try:

                        process_python_file(
                            file_path,
                            repo
                        )

                    except Exception as e:

                        print(
                            f"Error: {e}"
                        )

    print("=" * 60)
    print("REPOSITORIES INDEXED")
    print("=" * 60)

    print(
        f"\nTotal Chunks: {len(code_chunks)}"
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
{chunk["repo_name"]}

Team:
{chunk["team"]}

Framework:
{chunk["framework"]}

Architecture:
{chunk["architecture"]}

Language:
{chunk["language"]}

Type:
{chunk["type"]}

Name:
{chunk["name"]}

Imports:
{" ".join(chunk["imports"])}

Dependencies:
{" ".join(chunk["dependencies"])}

Docstring:
{chunk["docstring"]}

Code:
{chunk["content"]}
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

    print("Vectors uploaded.")

# =========================================================
# SAVE METADATA
# =========================================================

def save_metadata():

    with open(
        "data/repository_index.json",
        "w"
    ) as f:

        json.dump(
            code_chunks,
            f,
            indent=2
        )

    print("\nMetadata saved.")