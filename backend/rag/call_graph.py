# =========================================================
# UNIVERSAL CALL GRAPH BUILDER
# =========================================================

"""
Builds a language-agnostic call graph from the
normalized symbol model.

Works on:

Python
Java
JavaScript
TypeScript
Go
Rust
PHP
C#
Kotlin
Swift
and other Tree-Sitter languages.
"""

from collections import defaultdict

# =========================================================
# BUILD CALL GRAPH
# =========================================================

def build_call_graph(

    symbols

):

    graph = {

        "nodes": {},

        "edges": [],

        "adjacency": defaultdict(list)
    }

    functions = symbols.get(
        "functions",
        []
    )

    calls = symbols.get(
        "calls",
        []
    )

    function_lookup = {

        function.get(
           "qualified_name",
           function["name"]
       ): function

        for function in functions
    }

    # =============================================
    # REGISTER NODES
    # =============================================

    for function in functions:

        graph["nodes"][
            function["id"]
        ] = {

            "id":
            function["id"],

            "name":
            function["name"],

            "qualified_name":
            function.get(
               "qualified_name"
            ),

            "type":
            "FUNCTION",

            "start_line":
            function[
                "start_line"
            ],

            "end_line":
            function[
                "end_line"
            ]
        }

    # =============================================
    # BUILD EDGES
    # =============================================

    for function in functions:

        source_id = function[
            "id"
        ]

        source_name = function[
            "name"
        ]

        source_body = function[
            "content"
        ]

        for call in calls:

            call_name = call[
                "name"
            ]

            if not call_name:

                continue

            if call_name == source_name:

                continue

            if call_name not in source_body:

                continue

            target = function_lookup.get(
                call_name
            )

            if target is None:

                continue

            edge = {

                "source":
                source_id,

                "target":
                target["id"],

                "relation":
                "CALLS"
            }

            graph[
                "edges"
            ].append(
                edge
            )

            graph[
                "adjacency"

                
            ][
                source_id
            ].append(

                target["id"]
            )

    return graph

# =========================================================
# GET CALLEES
# =========================================================

def get_callees(

    graph,
    function_id

):

    return graph[
        "adjacency"
    ].get(

        function_id,

        []
    )

# =========================================================
# GET CALLERS
# =========================================================

def get_callers(

    graph,
    function_id

):

    callers = []

    for edge in graph[
        "edges"
    ]:

        if edge[
            "target"
        ] == function_id:

            callers.append(

                edge[
                    "source"
                ]
            )

    return callers

# =========================================================
# GET ROOT FUNCTIONS
# =========================================================

def get_root_functions(

    graph

):

    roots = []

    node_ids = set(

        graph[
            "nodes"
        ].keys()
    )

    called_nodes = set()

    for edge in graph[
        "edges"
    ]:

        called_nodes.add(

            edge[
                "target"
            ]
        )

    for node_id in node_ids:

        if node_id not in called_nodes:

            roots.append(
                node_id
            )

    return roots

# =========================================================
# GET LEAF FUNCTIONS
# =========================================================

def get_leaf_functions(

    graph

):

    leaves = []

    for node_id in graph[
        "nodes"
    ]:

        if len(

            graph[
                "adjacency"
            ].get(

                node_id,

                []
            )

        ) == 0:

            leaves.append(
                node_id
            )

    return leaves

# =========================================================
# FIND WORKFLOW PATHS
# =========================================================

def discover_workflows(

    graph

):

    workflows = []

    roots = get_root_functions(
        graph
    )

    for root in roots:

        workflow = []

        dfs(

            graph,

            root,

            workflow,

            workflows
        )

    return workflows

# =========================================================
# DFS WALK
# =========================================================

def dfs(

    graph,

    node,

    current_path,

    workflows

):

    current_path = current_path + [
        node
    ]

    children = graph[
        "adjacency"
    ].get(

        node,

        []
    )

    if len(children) == 0:

        workflows.append(
            current_path
        )

        return

    for child in children:

        dfs(

            graph,

            child,

            current_path,

            workflows
        )