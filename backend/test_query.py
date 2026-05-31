import sys

from qdrant_client import QdrantClient
from rag.embeddings import embedding_model
from rag.config import COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT


def get_qdrant_client():
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=5.0)
        client.get_collections()  # verify connection
        return client
    except Exception as e:
        print(f"[WARNING] Could not connect to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}: {e}")
        print("[INFO] Falling back to local disk Qdrant client at 'data/qdrant_db'.")
        return QdrantClient(path="data/qdrant_db")

def query(question: str, top_k: int = 5):
    """Encode *question* and retrieve the *top_k* most similar chunks from Qdrant.
    Prints each hit's payload (repo, file, type, name, etc.) and its similarity score.
    """
    # Generate embedding vector for the query
    vec = embedding_model.encode([question], convert_to_numpy=True)[0]
    # Connect to Qdrant (fallback to local if needed)
    client = get_qdrant_client()
    # Perform the similarity search using the modern Qdrant API
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vec,
        limit=top_k,
        with_payload=True,
    )

    if not results.points:
        print("No results found.")
        return

    for i, point in enumerate(results.points, start=1):
        print(f"--- Hit {i} (score: {point.score:.4f}) ---")
        for key, value in point.payload.items():
            print(f"{key}: {value}")
        print()


if __name__ == "__main__":
    # If a query is passed as command‑line arguments, use it; otherwise fall back to an interactive prompt.
    if len(sys.argv) >= 2:
        # Command‑line mode: combine all arguments into a single query string.
        question = " ".join(sys.argv[1:])
        query(question, top_k=5)
    else:
        # Interactive mode: repeatedly ask the user for a query until they type 'exit' or an empty line.
        print("Enter a query to search the indexed repository (type 'exit' or press Enter to quit).")
        while True:
            try:
                question = input("\nQuery> ").strip()
            except EOFError:
                # Handles Ctrl‑D (EOF) gracefully.
                break
            if not question or question.lower() == "exit":
                print("Goodbye!")
                break
            query(question, top_k=5)
