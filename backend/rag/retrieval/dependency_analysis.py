# =========================================================
# DEPENDENCY ANALYSIS
# =========================================================

from collections import deque

def analyze_dependencies(

    graph,

    start_node,

    max_depth=5

):

    dependencies = set()

    visited = set()

    queue = deque()

    queue.append(
        (start_node, 0)
    )

    visited.add(
        start_node
    )

    while queue:

        current_node, depth = queue.popleft()

        if depth >= max_depth:

            continue

        for edge in graph["edges"]:

            if edge.get(
                "relationship"
            ) != "CALLS":

                continue

            source = edge.get(
                "source"
            )

            target = edge.get(
                "target"
            )

            if source == current_node:

                if target not in visited:

                    visited.add(target)

                    dependencies.add(target)

                    queue.append(

                        (
                            target,
                            depth + 1
                        )
                    )

    return list(dependencies)
