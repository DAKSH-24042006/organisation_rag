# =========================================================
# GRAPH CHUNK EXPANSION
# =========================================================

from rag.graph.graph_storage import (
    load_graph
)

from rag.graph.knowledge_graph import (
    KnowledgeGraph
)

from rag.retrieval.neighbor_expansion import (
    expand_neighbors
)

import json

# =========================================================
# LOAD GRAPH
# =========================================================

GRAPH = load_graph(

    KnowledgeGraph,

    "data/repository_graph.json"

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

    qualified_name = chunk.get(
        "qualified_name"
    )

    if not qualified_name:

        continue

    # =====================================
    # PRIMARY LOOKUP
    # =====================================

    existing = chunk_lookup.get(
        qualified_name
    )

    if existing is None:

        chunk_lookup[
            qualified_name
        ] = chunk

    else:

        if (

            existing.get(
                "type"
            ) == "MODULE"

            and

            chunk.get(
                "type"
            ) != "MODULE"

        ):

            chunk_lookup[
                qualified_name
            ] = chunk

    # =====================================
    # NORMALIZED LOOKUP
    # =====================================

    normalized = qualified_name.replace(

        "orgatisation_rag.backend.",

        ""
    )

    existing = chunk_lookup.get(
        normalized
    )

    if existing is None:

        chunk_lookup[
            normalized
        ] = chunk

    else:

        if (

            existing.get(
                "type"
            ) == "MODULE"

            and

            chunk.get(
                "type"
            ) != "MODULE"

        ):

            chunk_lookup[
                normalized
            ] = chunk



# =========================================================
# EXPAND CHUNKS
# =========================================================

def expand_chunks(

    chunks,

    max_neighbors=20

):

    seed_nodes = []

    for chunk in chunks:

        qualified_name = chunk.get(
            "qualified_name"
       )

        if not qualified_name:

            continue

        normalized = qualified_name.replace(

            "orgatisation_rag.backend.",

            ""
        )

        seed_nodes.append(
            normalized
        )

    expanded_nodes = expand_neighbors(

        GRAPH,

        seed_nodes,

        max_neighbors=max_neighbors
    )

    expanded_chunks = []

    seen = set()

    # ==========================================
    # ORIGINAL CHUNKS
    # ==========================================

    for chunk in chunks:

        key = chunk.get(
            "qualified_name"
        )

        if not key:

            continue

        normalized = key.replace(

            "orgatisation_rag.backend.",

            ""
        )

        if normalized in seen:

            continue

        expanded_chunks.append(
            chunk
        )

        seen.add(
            normalized
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

        if node in seen:

            continue

        expanded_chunks.append(
            chunk
        )

        seen.add(
            node
        )

    return expanded_chunks