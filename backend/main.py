from rag.indexer import (
    index_repositories,
    build_documents,
    generate_embeddings,
    store_vectors,
    save_metadata
)

from rag.orchestrator import (
    orchestrate_query
)

# =========================================================
# ENTERPRISE AI CODING PLATFORM
# =========================================================

print("\n" + "=" * 80)

print("ENTERPRISE AI CODING PLATFORM")

print("=" * 80)

# =========================================================
# INDEX REPOSITORIES
# =========================================================

index_repositories()

# =========================================================
# BUILD DOCUMENTS
# =========================================================

documents, _ = build_documents()

# =========================================================
# GENERATE EMBEDDINGS
# =========================================================

embeddings = generate_embeddings(
    documents
)

# =========================================================
# STORE VECTORS
# =========================================================

store_vectors(embeddings)

# =========================================================
# SAVE METADATA
# =========================================================

save_metadata()

# =========================================================
# INTERACTIVE LOOP
# =========================================================

while True:

    query = input(
        "\nAsk Question ('exit' to quit): "
    )

    if query.lower() == "exit":
        break

    try:

        final_response = orchestrate_query(
            query
        )

        print("\n" + "=" * 80)

        print("FINAL RESPONSE")

        print("=" * 80)

        print(final_response)

    except Exception as e:

        print("\nORCHESTRATION ERROR:")

        print(str(e))

print("\nExiting Enterprise AI System.")