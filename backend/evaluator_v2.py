import json
import time
from pathlib import Path

from rag.retriever import (
    vector_search,
    bm25_search,
    hybrid_merge
)

# =========================================================
# HYBRID SEARCH
# =========================================================

def search(query, top_k=5):

    vector_results = vector_search(
        query,
        top_k=top_k * 2
    )

    bm25_results = bm25_search(
        query,
        top_k=top_k * 2
    )

    merged = hybrid_merge(
        vector_results,
        bm25_results
    )

    return merged[:top_k]


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

    results = search(
        query,
        top_k=5
    )

    latency_ms = (
        time.time()
        - start_time
    ) * 1000

    retrieved_files = []

    for chunk in results:

        retrieved_files.append(
            chunk.get(
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
# CATEGORY REPORT
# =========================================================

def category_report(
    results
):

    categories = {}

    for result in results:

        category = result[
            "category"
        ]

        if category not in categories:

            categories[
                category
            ] = []

        categories[
            category
        ].append(
            result
        )

    print("\n")
    print("=" * 60)
    print("CATEGORY BREAKDOWN")
    print("=" * 60)

    for category, items in categories.items():

        top3 = (
            sum(
                x["top3"]
                for x in items
            )
            /
            len(items)
        )

        coverage = (
            sum(
                x["coverage"]
                for x in items
                if x["coverage"]
                is not None
            )
            /
            len(items)
        )

        print(
            f"{category:<25}"
            f"Top3={top3*100:6.2f}%   "
            f"Coverage={coverage*100:6.2f}%"
        )


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
    print("HYBRID RETRIEVAL EVALUATION")
    print("=" * 60)

    print(
        f"\nQueries: {n}"
    )

    print(
        f"Top-1 Accuracy: "
        f"{top1_acc*100:.2f}%"
    )

    print(
        f"Top-3 Accuracy: "
        f"{top3_acc*100:.2f}%"
    )

    print(
        f"Top-5 Accuracy: "
        f"{top5_acc*100:.2f}%"
    )

    print(
        f"Average Coverage: "
        f"{avg_coverage*100:.2f}%"
    )

    print(
        f"Average Latency: "
        f"{avg_latency:.2f} ms"
    )

    category_report(
        results
    )


# =========================================================
# MAIN
# =========================================================

def main():

    benchmark_file = Path(
        "evaluation/benchmark.json"
    )

    with open(
        benchmark_file,
        "r",
        encoding="utf-8"
    ) as f:

        benchmark = json.load(f)

    results = []

    print(
        "\nRunning HYBRID benchmark...\n"
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
        "hybrid_results.json"
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
        f"\nSaved results to:\n"
        f"{output_file}"
    )


if __name__ == "__main__":
    main()