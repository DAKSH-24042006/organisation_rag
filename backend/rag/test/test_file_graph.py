# =========================================================
# TEST FILE GRAPH
# =========================================================

from rag.graph.graph_builder import (
    build_graph_from_chunks
)

# =========================================================
# SAMPLE CHUNKS
# =========================================================

chunks = [

    {
        "name": "create_user",

        "type": "FUNCTION",

        "file": "user_service.py",

        "path": "services/user_service.py",

        "start_line": 1,

        "end_line": 10,

        "imports": [

            "save_user",

            "find_user"
        ]
    },

    {
        "name": "validate_user",

        "type": "FUNCTION",

        "file": "user_service.py",

        "path": "services/user_service.py",

        "start_line": 12,

        "end_line": 18,

        "imports": []
    }
]

# =========================================================
# BUILD GRAPH
# =========================================================

graph = build_graph_from_chunks(
    chunks
)

# =========================================================
# RESULTS
# =========================================================

print("\n========== SUMMARY ==========\n")

print(
    graph.summary()
)

print("\n========== NODES ==========\n")

for node_id, node in graph.nodes.items():

    print(node)

print("\n========== EDGES ==========\n")

for edge in graph.edges:

    print(edge)

print("\n========== NEIGHBORS ==========\n")

print(
    graph.get_neighbors(
        "services/user_service.py"
    )
)