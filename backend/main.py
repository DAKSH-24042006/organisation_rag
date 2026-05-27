from rag.indexer import (

    index_repositories,
    build_documents,
    generate_embeddings,
    store_vectors,
    save_metadata
)

from rag.retriever import retrieve

# =========================================================
# INDEXING PIPELINE
# =========================================================

print("\nStarting indexing pipeline...\n")

index_repositories()

print("\nBuilding documents...\n")

documents, bm25_corpus = build_documents()

embeddings = generate_embeddings(
    documents
)

store_vectors(embeddings)

save_metadata()

print("\nIndexing completed successfully.\n")

# =========================================================
# INTERACTIVE QUERY LOOP
# =========================================================

while True:

    query = input(
        "\nAsk Question ('exit' to quit): "
    )

    if query.lower() == "exit":
        break

    context = retrieve(query)

    print("\n" + "=" * 60)

    print("RETRIEVED CONTEXT")

    print("=" * 60)

    print(context)