# =========================================================
# REPOSITORY CALL RESOLVER
# =========================================================

from rag.call_resolver import (
    resolve_call
)

# =========================================================
# BUILD CALL EDGES
# =========================================================

def build_call_edges(

    symbols,

    symbol_index

):

    edges = []

    functions = symbols.get(
        "functions",
        []
    )

    calls = symbols.get(
        "calls",
        []
    )

    for function in functions:

        function_start = function[
            "start_line"
        ]

        function_end = function[
            "end_line"
        ]

        for call in calls:

            call_line = call[
                "start_line"
            ]

            if not (

                function_start
                <=
                call_line
                <=
                function_end

            ):
                continue

            resolved = resolve_call(

                call,

                symbol_index
            )

            if not resolved:
                continue

            edges.append(

                {

                    "source":
                    function[
                        "qualified_name"
                    ],

                    "target":
                    resolved[
                        "qualified_name"
                    ],

                    "relationship":
                    "CALLS"
                }

            )

    return edges
