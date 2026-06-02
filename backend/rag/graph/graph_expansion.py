# =========================================================
# GRAPH EXPANSION
# =========================================================

def expand_results(

    graph,
    initial_nodes,
    max_hops=1

):

    expanded = set(
        initial_nodes
    )

    frontier = set(
        initial_nodes
    )

    # =====================================================
    # HOP EXPANSION
    # =====================================================

    for _ in range(
        max_hops
    ):

        next_frontier = set()

        for node in frontier:

            neighbors = graph.get_neighbors(
                node
            )

            for neighbor in neighbors:

                neighbor_node = neighbor[
                    "node"
                ]

                if neighbor_node not in expanded:

                    expanded.add(
                        neighbor_node
                    )

                    next_frontier.add(
                        neighbor_node
                    )

        frontier = next_frontier

    return list(
        expanded
    )