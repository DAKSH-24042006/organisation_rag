# =========================================================
# REPOSITORY GRAPH BUILDER
# =========================================================

import json

from rag.graph.graph_builder import (
    build_graph_from_chunks
)

from rag.graph.graph_storage import (
    save_graph
)

# =========================================================
# BUILD REPOSITORY GRAPH
# =========================================================

def build_repository_graph(

    index_path="data/repository_index.json"

):

    with open(

        index_path,

        "r",

        encoding="utf-8"

    ) as f:

        chunks = json.load(f)

    graph = build_graph_from_chunks(
        chunks
    )

    save_graph(

        graph,

        "data/repository_graph.json"

    )

    return graph