# =========================================================
# UNIVERSAL KNOWLEDGE GRAPH
# =========================================================

import json

from collections import defaultdict

# =========================================================
# LOAD INDEX
# =========================================================

with open(
    "data/repository_index.json",
    "r",
    encoding="utf-8"
) as f:

    code_chunks = json.load(f)

# =========================================================
# GRAPH STORAGE
# =========================================================

knowledge_graph = {

    "nodes": {},

    "edges": [],

    "adjacency": defaultdict(list)
}

# =========================================================
# ADD NODE
# =========================================================

def add_node(

    node_id,
    node_type,
    metadata

):

    if node_id not in knowledge_graph["nodes"]:

        knowledge_graph[
            "nodes"
        ][node_id] = {

            "type":
            node_type,

            "metadata":
            metadata
        }

# =========================================================
# ADD EDGE
# =========================================================

def add_edge(

    source,
    target,
    relation

):

    edge = {

        "source":
        source,

        "target":
        target,

        "relation":
        relation
    }

    knowledge_graph[
        "edges"
    ].append(edge)

    knowledge_graph[
        "adjacency"
    ][source].append(target)

# =========================================================
# NODE ID
# =========================================================

def build_node_id(

    chunk

):

    return (

        chunk["path"]
        + "::"
        + chunk["name"]
    )

# =========================================================
# SYMBOL GRAPH
# =========================================================

def build_symbol_graph():

    print(
        "\nBuilding Symbol Graph..."
    )

    for chunk in code_chunks:

        node_id = build_node_id(
            chunk
        )

        add_node(

            node_id,

            chunk.get(
                "type",
                "unknown"
            ),

            chunk
        )

# =========================================================
# IMPORT GRAPH
# =========================================================

def build_import_graph():

    print(
        "\nBuilding Import Graph..."
    )

    for chunk in code_chunks:

        source = build_node_id(
            chunk
        )

        imports = chunk.get(
            "imports",
            []
        )

        for imp in imports:

            target = (
                "import::"
                + str(imp)
            )

            add_node(

                target,

                "IMPORT",

                {}
            )

            add_edge(

                source,

                target,

                "IMPORTS"
            )

# =========================================================
# CALL GRAPH
# =========================================================

def build_call_graph():

    print(
        "\nBuilding Call Graph..."
    )

    lookup = {}

    for chunk in code_chunks:

        lookup[
            chunk["name"]
        ] = build_node_id(
            chunk
        )

    for chunk in code_chunks:

        source = build_node_id(
            chunk
        )

        calls = chunk.get(
            "calls",
            []
        )

        for call in calls:

            target = lookup.get(
                call
            )

            if target:

                add_edge(

                    source,

                    target,

                    "CALLS"
                )

# =========================================================
# FILE DEPENDENCY GRAPH
# =========================================================

def build_file_dependency_graph():

    print(
        "\nBuilding File Dependency Graph..."
    )

    file_nodes = {}

    for chunk in code_chunks:

        file_name = chunk["path"]

        if file_name not in file_nodes:

            file_nodes[
                file_name
            ] = (

                "file::"
                + file_name
            )

            add_node(

                file_nodes[
                    file_name
                ],

                "FILE",

                {
                    "path":
                    file_name
                }
            )

    for chunk in code_chunks:

        symbol_node = build_node_id(
            chunk
        )

        file_node = (

            "file::"
            + chunk["path"]
        )

        add_edge(

            file_node,

            symbol_node,

            "CONTAINS"
        )

# =========================================================
# BUSINESS GRAPH
# =========================================================

def build_business_graph():

    print(
        "\nBuilding Business Graph..."
    )

    for chunk in code_chunks:

        role = chunk.get(

            "business_role",

            "general_service"
        )

        role_node = (

            "role::"
            + role
        )

        add_node(

            role_node,

            "BUSINESS_ROLE",

            {
                "role":
                role
            }
        )

        symbol_node = build_node_id(
            chunk
        )

        add_edge(

            role_node,

            symbol_node,

            "OWNS"
        )

# =========================================================
# SEMANTIC GRAPH
# =========================================================

def build_semantic_graph():

    print(
        "\nBuilding Semantic Graph..."
    )

    for chunk in code_chunks:

        source = build_node_id(
            chunk
        )

        tags = set(

            chunk.get(
                "semantic_tags",
                []
            )
        )

        if len(tags) == 0:

            continue

        for other in code_chunks:

            if chunk == other:

                continue

            overlap = tags.intersection(

                set(

                    other.get(
                        "semantic_tags",
                        []
                    )
                )
            )

            if len(overlap) == 0:

                continue

            target = build_node_id(
                other
            )

            add_edge(

                source,

                target,

                "SEMANTICALLY_RELATED"
            )

# =========================================================
# BUILD KNOWLEDGE GRAPH
# =========================================================

def build_knowledge_graph():

    print(
        "\nBuilding Knowledge Graph...\n"
    )

    build_symbol_graph()

    build_import_graph()

    build_call_graph()

    build_file_dependency_graph()

    build_business_graph()

    build_semantic_graph()

    print(
        "\nKnowledge Graph Built Successfully."
    )

# =========================================================
# GET NEIGHBORS
# =========================================================

def get_neighbors(

    node_id

):

    return knowledge_graph[
        "adjacency"
    ].get(

        node_id,

        []
    )

# =========================================================
# SAVE GRAPH
# =========================================================

def save_graph():

    with open(

        "data/knowledge_graph.json",

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            {

                "nodes":
                knowledge_graph[
                    "nodes"
                ],

                "edges":
                knowledge_graph[
                    "edges"
                ]
            },

            f,

            indent=2
        )

    print(
        "\nKnowledge Graph Saved."
    )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    build_knowledge_graph()

    save_graph()

    print("\nGRAPH SUMMARY\n")

    print(

        f"Nodes: "
        f"{len(knowledge_graph['nodes'])}"
    )

    print(

        f"Edges: "
        f"{len(knowledge_graph['edges'])}"
    )