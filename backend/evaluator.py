import json
import time
from pathlib import Path

from qdrant_client import QdrantClient

from rag.embeddings import embedding_model
from rag.config import (
    COLLECTION_NAME,
    QDRANT_HOST,
    QDRANT_PORT
)

# =========================================================
# GLOBAL QDRANT CLIENT
# =========================================================

CLIENT = None


# =========================================================
# QDRANT CONNECTION
# =========================================================

def get_qdrant_client():

    global CLIENT

    if CLIENT is not None:
        return CLIENT

    try:

        CLIENT = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            timeout=5.0
        )

        CLIENT.get_collections()

        return CLIENT

    except Exception as e:

        print(
            f"[WARNING] Could not connect to Qdrant at "
            f"{QDRANT_HOST}:{QDRANT_PORT}: {e}"
        )

        print(
            "[INFO] Falling back to local disk Qdrant client."
        )

        CLIENT = QdrantClient(
            path="data/qdrant_db"
        )

        return CLIENT

   
   

# =========================================================
# RETRIEVAL
# =========================================================

def search(query: str, top_k: int = 5):

    client = get_qdrant_client()

    vec = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )[0]

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vec,
        limit=top_k,
        with_payload=True,
    )

    return results.points


# =========================================================
# COVERAGE
# =========================================================

def compute_coverage(
    expected_files,
    retrieved_files
):

    if not expected_files:
        return None

    matches = len(
        set(expected_files)
        &
        set(retrieved_files)
    )

    return matches / len(expected_files)


# =========================================================
# SINGLE QUERY EVALUATION
# =========================================================

def evaluate_query(
    test_case
):

    query = test_case["query"]

    expected_files = test_case[
        "expected_files"
    ]

    expected_top1 = test_case.get(
        "expected_top1"
    )

    start_time = time.time()

    results = search(query)

    latency_ms = (
        time.time()
        - start_time
    ) * 1000

    retrieved_files = []

    for hit in results:

        payload = hit.payload

        retrieved_files.append(
            payload.get(
                "file",
                ""
            )
        )

    top1 = 0
    top3 = 0
    top5 = 0

    if (
        expected_top1
        and
        len(retrieved_files) > 0
        and
        retrieved_files[0]
        == expected_top1
    ):
        top1 = 1

    if any(
        f in retrieved_files[:3]
        for f in expected_files
    ):
        top3 = 1

    if any(
        f in retrieved_files[:5]
        for f in expected_files
    ):
        top5 = 1

    coverage = compute_coverage(
        expected_files,
        retrieved_files
    )

    return {

        "id":
            test_case["id"],

        "query":
            query,

        "category":
            test_case["category"],

        "difficulty":
            test_case["difficulty"],

        "top1":
            top1,

        "top3":
            top3,

        "top5":
            top5,

        "coverage":
            coverage,

        "latency_ms":
            round(
                latency_ms,
                2
            ),

        "retrieved_files":
            retrieved_files
    }


# =========================================================
# REPORT
# =========================================================

def print_report(
    results
):

    n = len(results)

    top1_acc = (
        sum(r["top1"] for r in results)
        / n
    )

    top3_acc = (
        sum(r["top3"] for r in results)
        / n
    )

    top5_acc = (
        sum(r["top5"] for r in results)
        / n
    )

    coverage_values = [

        r["coverage"]

        for r in results

        if r["coverage"]
        is not None
    ]

    avg_coverage = (
        sum(coverage_values)
        / len(coverage_values)
    )

    avg_latency = (
        sum(
            r["latency_ms"]
            for r in results
        )
        / n
    )

    print("\n")
    print("=" * 60)
    print("ORGANIZATION RAG EVALUATION REPORT")
    print("=" * 60)

    print(
        f"\nQueries: {n}"
    )

    print(
        f"Top-1 Accuracy: "
        f"{top1_acc * 100:.2f}%"
    )

    print(
        f"Top-3 Accuracy: "
        f"{top3_acc * 100:.2f}%"
    )

    print(
        f"Top-5 Accuracy: "
        f"{top5_acc * 100:.2f}%"
    )

    print(
        f"Average Coverage: "
        f"{avg_coverage * 100:.2f}%"
    )

    print(
        f"Average Latency: "
        f"{avg_latency:.2f} ms"
    )

    print("\n")


# =========================================================
# MAIN
# =========================================================

def main():

    benchmark_file = Path(
        "evaluation/benchmark.json"
    )

    if not benchmark_file.exists():

        raise FileNotFoundError(
            f"Benchmark file not found: "
            f"{benchmark_file}"
        )

    with open(
        benchmark_file,
        "r",
        encoding="utf-8"
    ) as f:

        benchmark = json.load(f)

    results = []

    print(
        "\nRunning benchmark...\n"
    )

    for test_case in benchmark:

        result = evaluate_query(
            test_case
        )

        results.append(
            result
        )

        print(
            f"[{test_case['id']:02d}] "
            f"{test_case['query']}"
        )

    print_report(
        results
    )

    results_dir = Path(
        "evaluation/results"
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        results_dir
        /
        "evaluation_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=4
        )

    print(
        f"Results saved to:\n"
        f"{output_file}"
    )


if __name__ == "__main__":
    main()