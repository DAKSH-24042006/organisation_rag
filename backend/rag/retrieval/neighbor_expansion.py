# =========================================================
# GRAPH NEIGHBOR EXPANSION
# =========================================================

def expand_neighbors(

    graph,

    seed_nodes,

    max_neighbors=10

):

    expanded = set()

    for node in seed_nodes:

        expanded.add(
            node
        )

    count = 0

    # =====================================
    # KNOWLEDGE GRAPH OBJECT
    # =====================================

    for edge in graph.edges:

        source = getattr(
            edge,
            "source",
            None
        )

        target = getattr(
            edge,
            "target",
            None
        )

        if (
            source in seed_nodes
            or target in seed_nodes
        ):

            expanded.add(
                source
            )

            expanded.add(
                target
            )

            count += 1

            if count >= max_neighbors:

                break

    return list(
        expanded
    )