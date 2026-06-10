# =========================================================
# Organization RAG Entry Point (V2)
# =========================================================

import sys
from rag.indexer import run_indexing_pipeline

def main():
    print("\nStarting Code RAG V2 Builder...\n")
    try:
        run_indexing_pipeline()
        print("\nCode RAG V2 Build Complete Successfully.\n")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Index pipeline failed: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()