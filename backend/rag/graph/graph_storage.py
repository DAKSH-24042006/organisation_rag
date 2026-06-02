# =========================================================
# GRAPH STORAGE
# =========================================================

import json

# =========================================================
# SAVE GRAPH
# =========================================================

def save_graph(

    graph,
    path="data/knowledge_graph.json"

):

    data = {

        "nodes": graph.nodes,

        "edges": graph.edges
    }

    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            data,

            f,

            indent=2
        )

# =========================================================
# LOAD GRAPH
# =========================================================

def load_graph(

    graph_class,
    path="data/knowledge_graph.json"

):

    with open(

        path,

        "r",

        encoding="utf-8"

    ) as f:

        data = json.load(f)

    graph = graph_class()

    graph.nodes = data.get(
        "nodes",
        {}
    )

    graph.edges = data.get(
        "edges",
        []
    )

    return graph