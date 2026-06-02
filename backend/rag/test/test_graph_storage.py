from rag.graph.knowledge_graph import (
    KnowledgeGraph
)

from rag.graph.graph_storage import (

    save_graph,

    load_graph
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

save_graph(graph)

loaded = load_graph(
    KnowledgeGraph
)

print(
    loaded.nodes
)

print(
    loaded.edges
)