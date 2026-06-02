from rag.graph.graph_builder import (
    build_knowledge_graph
)

symbols = {

    "all_symbols": [

        {
            "name": "create_user",
            "symbol_type": "FUNCTION"
        },

        {
            "name": "save_user",
            "symbol_type": "FUNCTION"
        }
    ]
}

call_graph = {

    "create_user": [

        "save_user"
    ]
}

graph = build_knowledge_graph(

    symbols,

    call_graph
)

print(
    graph.summary()
)

print(
    graph.nodes
)

print(
    graph.edges
)