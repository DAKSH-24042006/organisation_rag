# =========================================================
# REPOSITORY IMPORT GRAPH
# =========================================================

from rag.import_resolver import (
    resolve_python_import
)

# =========================================================
# BUILD IMPORT EDGES
# =========================================================

def build_import_edges(

    chunks,
    repository_root

):

    edges = []

    print("\nTOTAL CHUNKS:", len(chunks))

    for chunk in chunks:

        print(
            "\nCHUNK:",
            chunk.get("type"),
            "|",
            chunk.get("name")
        )

        source_file = chunk.get(
            "path"
        )

        import_module = chunk.get(
            "import_module"
        )

        print(
            "IMPORT MODULE:",
            import_module
        )

        if not import_module:

            continue

        resolved = resolve_python_import(

            import_module,

            repository_root
        )

        print(
            "RESOLVED:",
            resolved
        )

        if not resolved:

            continue

        edges.append(

            {

                "source":
                source_file,

                "target":
                resolved,

                "relationship":
                "IMPORTS"
            }
        )

        print(
            "EDGE CREATED"
        )

    return edges