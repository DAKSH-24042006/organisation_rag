from rag.graph.knowledge_graph import (
    KnowledgeGraph
)

graph = KnowledgeGraph()

graph.add_node(
    "create_user",
    "FUNCTION"
)

graph.add_node(
    "save_user",
    "FUNCTION"
)

graph.add_edge(
    "create_user",
    "save_user",
    "CALLS"
)

print(
    graph.summary()
)

print(
    graph.get_neighbors(
        "create_user"
    )
)

print(
    graph.get_node(
        "create_user"
    )
)

print(
    graph.num_nodes()
)

print(
    graph.num_edges()
)