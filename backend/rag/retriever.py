# =========================================================
# retriever.py
# =========================================================

import json
import numpy as np

from rank_bm25 import BM25Okapi

from qdrant_client import QdrantClient

from rag.embeddings import embedding_model

from rag.config import (

    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME
)

# =========================================================
# QDRANT CLIENT
# =========================================================

client = QdrantClient(

    host=QDRANT_HOST,

    port=QDRANT_PORT
)

# =========================================================
# LOAD METADATA
# =========================================================

with open(

    "data/repository_index.json",

    "r",

    encoding="utf-8"

) as f:

    code_chunks = json.load(f)

# =========================================================
# BUILD BM25 INDEX
# =========================================================

bm25_corpus = []

for chunk in code_chunks:

    text = (

        chunk.get("search_text", "")
        + " "
        + chunk.get("summary", "")
        + " "
        + " ".join(
            chunk.get("semantic_tags", [])
        )
        + " "
        + chunk.get("content", "")
    )

    tokens = text.lower().split()

    bm25_corpus.append(tokens)

bm25 = BM25Okapi(bm25_corpus)

# =========================================================
# QUERY UNDERSTANDING
# =========================================================

def understand_query(query):

    query_lower = query.lower()

    semantic_tags = []

    architecture = None

    business_roles = []

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    auth_keywords = [

        "jwt",
        "token",
        "auth",
        "authentication",
        "login",
        "signup",
        "security",
        "session"
    ]

    # =====================================================
    # DATABASE
    # =====================================================

    db_keywords = [

        "database",
        "sql",
        "query",
        "orm",
        "model",
        "postgres",
        "mysql",
        "mongodb"
    ]

    # =====================================================
    # API
    # =====================================================

    api_keywords = [

        "api",
        "endpoint",
        "route",
        "request",
        "response",
        "backend"
    ]

    # =====================================================
    # CACHE
    # =====================================================

    cache_keywords = [

        "redis",
        "cache",
        "caching"
    ]

    # =====================================================
    # FRONTEND
    # =====================================================

    frontend_keywords = [

        "react",
        "frontend",
        "component",
        "ui",
        "dashboard",
        "hook"
    ]

    # =====================================================
    # AUTH DETECTION
    # =====================================================

    if any(

        word in query_lower

        for word in auth_keywords
    ):

        semantic_tags.extend([

            "authentication",
            "security",
            "jwt"
        ])

        business_roles.append(
            "authentication_service"
        )

    # =====================================================
    # DATABASE DETECTION
    # =====================================================

    if any(

        word in query_lower

        for word in db_keywords
    ):

        semantic_tags.extend([

            "database",
            "data_access"
        ])

        business_roles.append(
            "database_service"
        )

    # =====================================================
    # API DETECTION
    # =====================================================

    if any(

        word in query_lower

        for word in api_keywords
    ):

        semantic_tags.extend([

            "api",
            "backend"
        ])

        business_roles.append(
            "api_service"
        )

        architecture = "backend"

    # =====================================================
    # CACHE DETECTION
    # =====================================================

    if any(

        word in query_lower

        for word in cache_keywords
    ):

        semantic_tags.extend([

            "cache",
            "redis",
            "performance"
        ])

        business_roles.append(
            "cache_service"
        )

    # =====================================================
    # FRONTEND DETECTION
    # =====================================================

    if any(

        word in query_lower

        for word in frontend_keywords
    ):

        semantic_tags.extend([

            "frontend",
            "react",
            "ui"
        ])

        architecture = "frontend"

    semantic_tags = list(
        set(semantic_tags)
    )

    return {

        "query": query,

        "semantic_tags": semantic_tags,

        "business_roles": business_roles,

        "architecture": architecture
    }

# =========================================================
# BUILD ENHANCED QUERY
# =========================================================

def build_enhanced_query(query_data):

    enhanced_query = f"""

User Request:
{query_data['query']}

Semantic Intent:
{' '.join(query_data['semantic_tags'])}

Business Roles:
{' '.join(query_data['business_roles'])}

Architecture:
{query_data['architecture']}
"""

    return enhanced_query

# =========================================================
# VECTOR SEARCH
# =========================================================

def vector_search(

    query,
    top_k=10
):

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_embedding,

        limit=top_k
    )

    formatted_results = []

    for result in results.points:

        payload = result.payload

        payload["vector_score"] = result.score

        formatted_results.append(payload)

    return formatted_results

# =========================================================
# BM25 SEARCH
# =========================================================

def bm25_search(

    query,
    top_k=10
):

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked_indices = np.argsort(scores)[::-1]

    results = []

    for idx in ranked_indices[:top_k]:

        chunk = code_chunks[idx].copy()

        chunk["bm25_score"] = float(
            scores[idx]
        )

        results.append(chunk)

    return results

# =========================================================
# HYBRID MERGING
# =========================================================

def hybrid_merge(

    vector_results,
    bm25_results
):

    merged = {}

    # =====================================================
    # VECTOR RESULTS
    # =====================================================

    for chunk in vector_results:

        key = (

            chunk["name"]
            + chunk["path"]
        )

        merged[key] = chunk

        merged[key]["hybrid_score"] = (

            chunk.get("vector_score", 0) * 0.7
        )

    # =====================================================
    # BM25 RESULTS
    # =====================================================

    for chunk in bm25_results:

        key = (

            chunk["name"]
            + chunk["path"]
        )

        if key not in merged:

            merged[key] = chunk

            merged[key]["hybrid_score"] = 0

        merged[key]["hybrid_score"] += (

            chunk.get("bm25_score", 0) * 0.3
        )

    # =====================================================
    # SORT
    # =====================================================

    merged_results = sorted(

        merged.values(),

        key=lambda x: x[
            "hybrid_score"
        ],

        reverse=True
    )

    return merged_results

# =========================================================
# METADATA FILTERING
# =========================================================

def filter_results(

    results,
    query_data
):

    filtered = []

    for chunk in results:

        score_bonus = 0

        # =================================================
        # TAG MATCHING
        # =================================================

        chunk_tags = set(

            chunk.get(
                "semantic_tags",
                []
            )
        )

        query_tags = set(
            query_data[
                "semantic_tags"
            ]
        )

        overlap = len(

            chunk_tags.intersection(
                query_tags
            )
        )

        score_bonus += overlap * 0.2

        # =================================================
        # ROLE MATCHING
        # =================================================

        if (

            chunk.get(
                "business_role"
            )

            in

            query_data[
                "business_roles"
            ]
        ):

            score_bonus += 0.5

        # =================================================
        # WORKFLOW BOOSTING
        # =================================================

        workflows = chunk.get(
            "workflows",
            []
        )

        query_lower = query_data[
            "query"
        ].lower()

        if any(

            word in query_lower

            for word in [

                "login",
                "authentication",
                "session",
                "auth"
            ]
        ):

            if any(

                workflow in workflows

                for workflow in [

                    "login_flow",
                    "session_restore",
                    "auth_context"
                ]
            ):

                score_bonus += 3

                
        # =================================================
        # FINAL SCORE
        # =================================================

        chunk["final_score"] = (

            chunk.get(
                "hybrid_score",
                0
            )

            + score_bonus
        )

        filtered.append(chunk)

    filtered = sorted(

        filtered,

        key=lambda x: x[
            "final_score"
        ],

        reverse=True
    )

    return filtered

# =========================================================
# CONTEXT BUILDER
# =========================================================

def build_context(

    retrieved_chunks,
    max_chunks=5
):

    context = ""

    for chunk in retrieved_chunks[:max_chunks]:

        chunk_context = f"""

==================================================
FILE:
{chunk['file']}

FUNCTION / CLASS:
{chunk['name']}

BUSINESS ROLE:
{chunk['business_role']}

SEMANTIC TAGS:
{' '.join(chunk['semantic_tags'])}

SUMMARY:
{chunk['summary']}

CODE:
{chunk['content']}
==================================================

"""

        context += chunk_context

    return context

# =========================================================
# MAIN RETRIEVAL PIPELINE
# =========================================================

def retrieve_relevant_code(

    user_query,
    top_k=10
):

    print("\nUNDERSTANDING QUERY...\n")

    query_data = understand_query(
        user_query
    )

    enhanced_query = build_enhanced_query(
        query_data
    )

    print("\nRUNNING VECTOR SEARCH...\n")

    vector_results = vector_search(

        enhanced_query,

        top_k=top_k
    )

    print("\nRUNNING BM25 SEARCH...\n")

    bm25_results = bm25_search(

        enhanced_query,

        top_k=top_k
    )

    print("\nMERGING RESULTS...\n")

    merged_results = hybrid_merge(

        vector_results,
        bm25_results
    )

    print("\nFILTERING RESULTS...\n")

    filtered_results = filter_results(

        merged_results,
        query_data
    )

    print("\nBUILDING CONTEXT...\n")

    context = build_context(
        filtered_results
    )

    return {

        "query_data": query_data,

        "retrieved_chunks":
        filtered_results,

        "context": context
    }

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    query = input(
        "\nEnter Query: "
    )

    results = retrieve_relevant_code(
        query
    )

    print("\n" + "=" * 80)

    print("QUERY UNDERSTANDING")

    print("=" * 80)

    print(

        json.dumps(

            results["query_data"],

            indent=2
        )
    )

    print("\n" + "=" * 80)

    print("TOP RETRIEVED RESULTS")

    print("=" * 80)

    for idx, chunk in enumerate(

        results[
            "retrieved_chunks"
        ][:5]

    ):

        print(f"\nRESULT {idx+1}")

        print(
            f"Name: {chunk['name']}"
        )

        print(
            f"File: {chunk['file']}"
        )

        print(
            f"Role: "
            f"{chunk['business_role']}"
        )

        print(
            f"Tags: "
            f"{chunk['semantic_tags']}"
        )

        print(
            f"Score: "
            f"{chunk['final_score']}"
        )

    print("\n" + "=" * 80)

    print("FINAL CONTEXT")

    print("=" * 80)

    print(results["context"])