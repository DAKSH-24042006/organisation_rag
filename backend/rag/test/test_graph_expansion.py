from rag.graph.knowledge_graph import (
    KnowledgeGraph
)

from rag.graph.graph_expansion import (
    expand_results
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

graph.add_node(
    "send_welcome_email",
    "FUNCTION"
)

graph.add_edge(

    "create_user",

    "save_user",

    "CALLS"
)

graph.add_edge(

    "create_user",

    "send_welcome_email",

    "CALLS"
)

results = expand_results(

    graph,

    ["create_user"]
)

print(results)