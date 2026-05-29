# =========================================================
# UNIVERSAL WORKFLOW ENGINE
# =========================================================

import json

from collections import defaultdict

# =========================================================
# LOAD KNOWLEDGE GRAPH
# =========================================================

with open(
    "data/knowledge_graph.json",
    "r",
    encoding="utf-8"
) as f:

    graph = json.load(f)

# =========================================================
# ADJACENCY
# =========================================================

adjacency = defaultdict(list)

for edge in graph["edges"]:

    if edge["relation"] == "CALLS":

        adjacency[
            edge["source"]
        ].append(

            edge["target"]
        )

# =========================================================
# ROOT DETECTION
# =========================================================

def find_roots():

    targets = set()

    for edge in graph["edges"]:

        if edge["relation"] == "CALLS":

            targets.add(
                edge["target"]
            )

    roots = []

    for node_id in graph["nodes"]:

        if node_id not in targets:

            roots.append(
                node_id
            )

    return roots

# =========================================================
# DFS
# =========================================================

def dfs(

    node,
    path,
    workflows

):

    path = path + [node]

    children = adjacency.get(
        node,
        []
    )

    if len(children) == 0:

        workflows.append(
            path
        )

        return

    for child in children:

        dfs(

            child,

            path,

            workflows
        )

# =========================================================
# DISCOVER WORKFLOWS
# =========================================================

def discover_workflows():

    workflows = []

    roots = find_roots()

    for root in roots:

        dfs(

            root,

            [],

            workflows
        )

    return workflows

# =========================================================
# WORKFLOW METADATA
# =========================================================

def workflow_to_metadata(

    workflow

):

    components = []

    for node in workflow:

        metadata = graph[
            "nodes"
        ][node][
            "metadata"
        ]

        components.append({

            "name":
            metadata.get(
                "name"
            ),

            "file":
            metadata.get(
                "file"
            ),

            "summary":
            metadata.get(
                "summary"
            ),

            "business_role":
            metadata.get(
                "business_role"
            )
        })

    return components

# =========================================================
# BUILD CONTEXT
# =========================================================

def build_workflow_context():

    workflows = discover_workflows()

    context = ""

    for idx, workflow in enumerate(

        workflows,
        start=1

    ):

        context += f"""

==================================================
WORKFLOW {idx}
==================================================

"""

        components = workflow_to_metadata(
            workflow
        )

        for component in components:

            context += f"""

NAME:
{component['name']}

FILE:
{component['file']}

ROLE:
{component['business_role']}

SUMMARY:
{component['summary']}

"""

    return context

# =========================================================
# SAVE WORKFLOWS
# =========================================================

def save_workflows():

    workflows = discover_workflows()

    workflow_data = []

    for workflow in workflows:

        workflow_data.append(

            workflow_to_metadata(
                workflow
            )
        )

    with open(

        "data/workflows.json",

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            workflow_data,

            f,

            indent=2
        )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    workflows = discover_workflows()

    print(

        f"\nDiscovered "
        f"{len(workflows)} "
        f"workflows.\n"
    )

    save_workflows()

    print(

        build_workflow_context()
    )