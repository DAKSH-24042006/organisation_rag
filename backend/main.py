# =========================================================
# Organization RAG Entry Point
# =========================================================

from rag.indexer import (
    scan_all_repositories,
    print_statistics,
    generate_embeddings,
    store_vectors,
    save_repository_index,
    save_statistics
)

# =========================================================
# MAIN
# =========================================================

def main():

    print("\nStarting Organization RAG...\n")

    scan_all_repositories()

    print_statistics()

    embeddings = generate_embeddings()

    store_vectors(embeddings)

    save_repository_index()

    save_statistics()

    print("\nOrganization RAG Build Complete.\n")


if __name__ == "__main__":
    main()