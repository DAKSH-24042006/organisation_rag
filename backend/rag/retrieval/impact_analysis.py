# =========================================================
# IMPACT ANALYSIS
# =========================================================

from collections import deque

def analyze_impact(

    graph,

    target_node,

    max_depth=5

):

    impacted = set()

    visited = set()

    queue = deque()

    queue.append(
        (target_node, 0)
    )

    visited.add(
        target_node
    )

    while queue:

        current_node, depth = queue.popleft()

        if depth >= max_depth:

            continue

        for edge in graph["edges"]:

            if edge.get(
                "relationship"
            ) != "USED_BY":

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

                    impacted.add(target)

                    queue.append(

                        (
                            target,
                            depth + 1
                        )
                    )

    return list(impacted)