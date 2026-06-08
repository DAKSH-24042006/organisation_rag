# =========================================================
# GRAPH AWARE RANKING
# =========================================================

def apply_graph_boost(

    chunks,

    expanded_nodes,

    boost=0.15

):

    ranked = []

    for chunk in chunks:

        score = chunk.get(
            "hybrid_score",
            0.0
        )

        qualified_name = chunk.get(
            "qualified_name"
        )

        normalized = None

        if qualified_name:

            normalized = qualified_name.replace(

                "orgatisation_rag.backend.",

                ""
            )

        if (
            normalized
            and normalized in expanded_nodes
        ):

            score += boost

        chunk["graph_score"] = score

        ranked.append(
            chunk
        )

    ranked.sort(

        key=lambda x: x.get(
            "graph_score",
            0
        ),

        reverse=True
    )

    return ranked


