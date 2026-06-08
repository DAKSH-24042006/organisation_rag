# =========================================================
# GRAPH AWARE RETRIEVER
# =========================================================

from rag.graph_storage import (
    load_graph
)

from rag.retrieval.neighbor_expansion import (
    expand_neighbors
)

# =========================================================
# LOAD GRAPH
# =========================================================

GRAPH = load_graph(
    "repository_graph.json"
)

# =========================================================
# GRAPH EXPANSION
# =========================================================

def graph_aware_expand(

    chunks,

    max_neighbors=20

):

    seed_nodes = []

    for chunk in chunks:

        qualified_name = chunk.get(
            "qualified_name"
        )

        if qualified_name:

            seed_nodes.append(
                qualified_name
            )

    expanded_nodes = expand_neighbors(

        GRAPH,

        seed_nodes,

        max_neighbors=max_neighbors
    )

    return expanded_nodes