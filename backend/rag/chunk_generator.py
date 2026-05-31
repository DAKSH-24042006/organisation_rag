# =========================================================
# UNIVERSAL CHUNK GENERATOR
# =========================================================

"""
Converts extracted symbols into
Organization-RAG chunks.

Pipeline:

AST
 ↓
Symbols
 ↓
Chunks
 ↓
Embeddings
"""

import os

# =========================================================
# SAFE CONTENT
# =========================================================

def clean_content(
    content,
    max_chars=1000
):

    if not content:

        return ""

    return content[:max_chars]

# =========================================================
# BASE CHUNK
# =========================================================

def create_chunk(

    *,
    chunk_type,
    symbol,
    language,
    file_path,
    repo_name

):

    return {

    "repo_name": repo_name,
    "language": language,
    "type": chunk_type,

    "name": symbol.get(
        "name",
        "unknown"
    ),

    "file": os.path.basename(
        file_path
    ),

    "path": file_path,

    "start_line": symbol.get(
        "start_line",
        0
    ),

    "end_line": symbol.get(
        "end_line",
        0
    ),

    # ==========================
    # FRAMEWORK METADATA
    # ==========================

    "framework":
    symbol.get("framework"),

    "component_type":
    symbol.get("component_type"),

    "service_type":
    symbol.get("service_type"),

    "route":
    symbol.get("route"),

    "http_method":
    symbol.get("http_method"),

    "decorators":
    symbol.get(
        "decorators",
        []
    ),

    "annotations":
    symbol.get(
        "annotations",
        []
    ),

    "hooks":
    symbol.get(
        "hooks",
        []
    ),

    "namespace":
    symbol.get(
        "namespace"
    ),

    "includes":
    symbol.get(
        "includes",
        []
    ),

    "stl_usage":
    symbol.get(
        "stl_usage",
        []
    ),

    "is_async":
    symbol.get(
        "is_async",
        False
    ),

    "content":
    clean_content(
        symbol.get(
            "content",
            ""
        )
    )
}

# =========================================================
# FUNCTION CHUNKS
# =========================================================

def generate_function_chunks(

    symbols,
    language,
    file_path,
    repo_name

):

    chunks = []

    for symbol in symbols.get(
        "functions",
        []
    ):

        chunks.append(

            create_chunk(

                chunk_type=
                "FUNCTION",

                symbol=symbol,

                language=
                language,

                file_path=
                file_path,

                repo_name=
                repo_name
            )
        )

    return chunks

# =========================================================
# REACT COMPONENT CHUNKS
# =========================================================

def generate_react_chunks(

    symbols,
    language,
    file_path,
    repo_name

):

    chunks = []

    for symbol in symbols.get(
        "react_components",
        []
    ):

        chunks.append(

            create_chunk(

                chunk_type=
                "REACT_COMPONENT",

                symbol=symbol,

                language=
                language,

                file_path=
                file_path,

                repo_name=
                repo_name
            )
        )

    return chunks

# =========================================================
# CLASS CHUNKS
# =========================================================

def generate_class_chunks(

    symbols,
    language,
    file_path,
    repo_name

):

    chunks = []

    for symbol in symbols.get(
        "classes",
        []
    ):

        chunks.append(

            create_chunk(

                chunk_type=
                "CLASS",

                symbol=symbol,

                language=
                language,

                file_path=
                file_path,

                repo_name=
                repo_name
            )
        )

    return chunks

# =========================================================
# MODULE CHUNKS
# =========================================================

def generate_module_chunks(

    symbols,
    language,
    file_path,
    repo_name

):

    chunks = []

    for symbol in symbols.get(
        "modules",
        []
    ):

        chunks.append(

            create_chunk(

                chunk_type=
                "MODULE",

                symbol=symbol,

                language=
                language,

                file_path=
                file_path,

                repo_name=
                repo_name
            )
        )

    return chunks

# =========================================================
# FILE FALLBACK
# =========================================================

def generate_file_chunk(

    source_code,
    language,
    file_path,
    repo_name

):

    return {

        "repo_name":
        repo_name,

        "language":
        language,

        "type":
        "FILE",

        "name":
        os.path.basename(
            file_path
        ),

        "file":
        os.path.basename(
            file_path
        ),

        "path":
        file_path,

        "start_line":
        1,

        "end_line":
        source_code.count(
            "\n"
        ) + 1,

        "content":
        clean_content(
            source_code
        )
    }

# =========================================================
# MAIN ENTRY
# =========================================================

def generate_chunks(

    symbols,
    source_code,
    language,
    file_path,
    repo_name

):

    chunks = []

    chunks.extend(

        generate_function_chunks(

            symbols,

            language,

            file_path,

            repo_name
        )
    )

    chunks.extend(

        generate_react_chunks(

            symbols,

            language,

            file_path,

            repo_name
        )
    )

    chunks.extend(

        generate_class_chunks(

            symbols,

            language,

            file_path,

            repo_name
        )
    )

    chunks.extend(

        generate_module_chunks(

            symbols,

            language,

            file_path,

            repo_name
        )
    )

    # =============================================
    # FALLBACK
    # =============================================

    if len(chunks) == 0:

        chunks.append(

            generate_file_chunk(

                source_code,

                language,

                file_path,

                repo_name
            )
        )

    return chunks