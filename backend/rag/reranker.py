# =========================================================
# reranker.py
# =========================================================

# =========================================================
# RERANK RESULTS
# =========================================================

def rerank_results(

    retrieved_chunks,
    query_data
):

    reranked = []

    query_tags = set(

        query_data.get(
            "semantic_tags",
            []
        )
    )

    for chunk in retrieved_chunks:

        score = chunk.get(
            "final_score",
            0
        )

        # =================================================
        # TAG OVERLAP BONUS
        # =================================================

        chunk_tags = set(

            chunk.get(
                "semantic_tags",
                []
            )
        )

        overlap = len(

            query_tags.intersection(
                chunk_tags
            )
        )

        score += overlap * 0.5

        # =================================================
        # BUSINESS ROLE BONUS
        # =================================================

        if (

            chunk.get(
                "business_role"
            )

            in

            query_data.get(
                "business_roles",
                []
            )
        ):

            score += 1

        # =================================================
        # CALL COMPLEXITY BONUS
        # =================================================

        score += len(

            chunk.get(
                "calls",
                []
            )
        ) * 0.05

        # =================================================
        # SUMMARY BONUS
        # =================================================

        summary = chunk.get(
            "summary",
            ""
        ).lower()

        for tag in query_tags:

            if tag in summary:
                score += 0.2

        chunk["rerank_score"] = score

        reranked.append(chunk)

    reranked = sorted(

        reranked,

        key=lambda x: x[
            "rerank_score"
        ],

        reverse=True
    )

    return reranked