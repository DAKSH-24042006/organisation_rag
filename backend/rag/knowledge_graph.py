# =========================================================
# knowledge_graph.py
# =========================================================

import json
from collections import defaultdict

# =========================================================
# LOAD METADATA
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

    "function_calls": defaultdict(list),

    "file_dependencies": defaultdict(list),

    "business_roles": defaultdict(list),

    "semantic_relationships": defaultdict(list)
}

# =========================================================
# BUILD FUNCTION CALL GRAPH
# =========================================================

def build_function_call_graph():

    for chunk in code_chunks:

        source = chunk.get("name")

        calls = chunk.get("calls", [])

        for call in calls:

            knowledge_graph[
                "function_calls"
            ][source].append(call)

# =========================================================
# BUILD FILE DEPENDENCY GRAPH
# =========================================================

def build_file_dependency_graph():

    for chunk in code_chunks:

        file_name = chunk.get("file")

        imports = chunk.get(
            "imports",
            []
        )

        for imp in imports:

            knowledge_graph[
                "file_dependencies"
            ][file_name].append(imp)

# =========================================================
# BUILD BUSINESS ROLE GRAPH
# =========================================================

def build_business_role_graph():

    for chunk in code_chunks:

        role = chunk.get(
            "business_role",
            "general_service"
        )

        knowledge_graph[
            "business_roles"
        ][role].append(

            chunk.get("name")
        )

# =========================================================
# BUILD SEMANTIC RELATIONSHIPS
# =========================================================

def build_semantic_relationships():

    for chunk in code_chunks:

        source = chunk.get("name")

        tags = chunk.get(
            "semantic_tags",
            []
        )

        for other_chunk in code_chunks:

            if source == other_chunk.get("name"):
                continue

            other_tags = other_chunk.get(
                "semantic_tags",
                []
            )

            overlap = set(tags).intersection(
                set(other_tags)
            )

            if len(overlap) > 0:

                knowledge_graph[
                    "semantic_relationships"
                ][source].append({

                    "target":
                    other_chunk.get("name"),

                    "shared_tags":
                    list(overlap)
                })

# =========================================================
# BUILD COMPLETE GRAPH
# =========================================================

def build_knowledge_graph():

    print("\nBuilding Knowledge Graph...\n")

    build_function_call_graph()

    build_file_dependency_graph()

    build_business_role_graph()

    build_semantic_relationships()

    print(
        "\nKnowledge Graph Built Successfully."
    )

# =========================================================
# GET RELATED FUNCTIONS
# =========================================================

def get_related_functions(function_name):

    return knowledge_graph[
        "function_calls"
    ].get(function_name, [])

# =========================================================
# GET RELATED SERVICES
# =========================================================

def get_related_services(role):

    return knowledge_graph[
        "business_roles"
    ].get(role, [])

# =========================================================
# GET SEMANTICALLY RELATED CHUNKS
# =========================================================

def get_semantic_relationships(name):

    return knowledge_graph[
        "semantic_relationships"
    ].get(name, [])

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

                k: dict(v)

                for k, v in knowledge_graph.items()
            },

            f,

            indent=2
        )

    print("\nKnowledge Graph Saved.")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    build_knowledge_graph()

    save_graph()

    print("\nGRAPH SUMMARY\n")

    print(
        f"Function Nodes: "
        f"{len(knowledge_graph['function_calls'])}"
    )

    print(
        f"Dependency Nodes: "
        f"{len(knowledge_graph['file_dependencies'])}"
    )