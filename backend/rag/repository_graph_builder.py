# =========================================================
# REPOSITORY GRAPH BUILDER
# =========================================================

# =========================================================
# BUILD GRAPH
# =========================================================

def build_repository_graph(

    chunks,

    import_edges,

    call_edges,

    used_by_edges

):

    graph = {

        "nodes": [],

        "edges": []
    }

    # =====================================================
    # NODES
    # =====================================================

    for chunk in chunks:

        graph[
            "nodes"
        ].append(

            {

                "id":
                chunk.get(
                    "qualified_name",
                    chunk.get(
                        "path"
                    )
                ),

                "type":
                chunk.get(
                    "type"
                ),

                "name":
                chunk.get(
                    "name"
                ),

                "path":
                chunk.get(
                    "path"
                )
            }

        )

    # =====================================================
    # EDGES
    # =====================================================

    graph[
        "edges"
    ].extend(

        import_edges
    )

    graph[
        "edges"
    ].extend(

        call_edges
    )

    graph[
        "edges"
    ].extend(

        used_by_edges
    )

    return graph