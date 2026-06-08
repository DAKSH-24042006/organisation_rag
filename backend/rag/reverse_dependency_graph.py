# =========================================================
# REVERSE DEPENDENCY GRAPH
# =========================================================

def build_used_by_edges(

    call_edges

):

    used_by_edges = []

    for edge in call_edges:

        if edge.get(
            "relationship"
        ) != "CALLS":

            continue

        used_by_edges.append(

            {

                "source":
                edge[
                    "target"
                ],

                "target":
                edge[
                    "source"
                ],

                "relationship":
                "USED_BY"
            }

        )

    return used_by_edges