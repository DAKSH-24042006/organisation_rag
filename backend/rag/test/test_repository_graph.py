from rag.graph.repository_graph_builder import (
    build_repository_graph
)

graph = build_repository_graph()

print(
    graph.summary()
)