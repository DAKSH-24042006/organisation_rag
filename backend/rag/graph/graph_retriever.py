# =========================================================
# GRAPH RETRIEVER
# =========================================================

from rag.graph.graph_storage import (
    load_graph
)

from rag.graph.knowledge_graph import (
    KnowledgeGraph
)

from rag.graph.graph_expansion import (
    expand_results
)

import json

# =========================================================
# LOAD REPOSITORY GRAPH
# =========================================================

repository_graph = load_graph(
    KnowledgeGraph
)

# =========================================================
# LOAD REPOSITORY INDEX
# =========================================================

with open(
    "data/repository_index.json",
    "r",
    encoding="utf-8"
) as f:

    repository_chunks = json.load(f)

# =========================================================
# CHUNK LOOKUP
# =========================================================

chunk_lookup = {}

for chunk in repository_chunks:

    name = chunk.get(
        "name"
    )

    if not name:
        continue

    chunk_lookup[name] = chunk

# =========================================================
# EXPAND RETRIEVAL RESULTS
# =========================================================

def graph_expand(

    chunks,

    max_hops=1

):

    initial_nodes = []

    for chunk in chunks:

        name = chunk.get(
            "name"
        )

        if name:

            initial_nodes.append(
                name
            )

    expanded_nodes = expand_results(

        repository_graph,

        initial_nodes,

        max_hops=max_hops
    )

    expanded_chunks = []

    seen = set()

    # ==========================================
    # ORIGINAL CHUNKS
    # ==========================================

    for chunk in chunks:

        key = (

            chunk.get(
                "path",
                ""
            )

            +

            chunk.get(
                "name",
                ""
            )
        )

        if key not in seen:

            expanded_chunks.append(
                chunk
            )

            seen.add(
                key
            )

    # ==========================================
    # GRAPH DISCOVERED CHUNKS
    # ==========================================

    for node in expanded_nodes:

        if node not in chunk_lookup:

            continue

        chunk = chunk_lookup[
            node
        ]

        key = (

            chunk.get(
                "path",
                ""
            )

            +

            chunk.get(
                "name",
                ""
            )
        )

        if key in seen:

            continue

        expanded_chunks.append(
            chunk
        )

        seen.add(
            key
        )

    return expanded_chunks