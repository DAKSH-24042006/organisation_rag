# =========================================================
# GRAPH TRAVERSAL
# =========================================================

from collections import deque

# =========================================================
# BFS TRAVERSAL
# =========================================================

def traverse_graph(

    graph,

    start_nodes,

    max_depth=2

):

    visited = set()

    queue = deque()

    results = set()

    for node in start_nodes:

        queue.append(
            (node, 0)
        )

        visited.add(node)

        results.add(node)

    while queue:

        current_node, depth = queue.popleft()

        if depth >= max_depth:

            continue

        for edge in graph["edges"]:

            source = edge.get(
                "source"
            )

            target = edge.get(
                "target"
            )

            if source == current_node:

                if target not in visited:

                    visited.add(target)

                    results.add(target)

                    queue.append(

                        (
                            target,
                            depth + 1
                        )
                    )

        # optional reverse traversal

            elif target == current_node:

                if source not in visited:

                    visited.add(source)

                    results.add(source)

                    queue.append(

                        (
                            source,
                            depth + 1
                        )
                    )

    return list(results)