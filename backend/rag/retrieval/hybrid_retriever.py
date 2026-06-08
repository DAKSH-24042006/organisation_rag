# =========================================================
# HYBRID RETRIEVER
# =========================================================

from rag.retrieval.neighbor_expansion import (
    expand_neighbors
)

# =========================================================
# HYBRID RETRIEVE
# =========================================================

def hybrid_retrieve(

    graph,

    retrieved_nodes,

    max_neighbors=10

):

    expanded_nodes = expand_neighbors(

        graph,

        retrieved_nodes,

        max_neighbors=max_neighbors
    )

    return expanded_nodes