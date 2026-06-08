# =========================================================
# GRAPH BUILDER
# =========================================================

from rag.graph.knowledge_graph import (
    KnowledgeGraph
)

# =========================================================
# BUILD KNOWLEDGE GRAPH
# =========================================================

def build_knowledge_graph(

    symbols,
    call_graph

):

    graph = KnowledgeGraph()

    # =====================================================
    # SYMBOL NODES
    # =====================================================

    for symbol in symbols.get(
        "all_symbols",
        []
    ):

        node_id = symbol.get(
            "qualified_name"
        )or symbol.get(
            "name"
        )

        if not node_id:

            continue

        graph.add_node(

            node_id,

            symbol.get(
                "symbol_type",
                "UNKNOWN"
            ),

            start_line=symbol.get(
                "start_line"
            ),

            end_line=symbol.get(
                "end_line"
            )
        )

    # =====================================================
    # CALL GRAPH EDGES
    # =====================================================

    if isinstance(
        call_graph,
        dict
    ):

        for caller, callees in call_graph.items():

            for callee in callees:

                graph.add_edge(

                    caller,

                    callee,

                    "CALLS"
                )

    return graph


# =========================================================
# BUILD GRAPH FROM CHUNKS
# =========================================================

def build_graph_from_chunks(

    chunks

):

    graph = KnowledgeGraph()

    # =====================================================
    # FILE NODES
    # =====================================================

    created_files = set()

    for chunk in chunks:

        file_path = chunk.get(
            "path"
        )

        if not file_path:

            continue

        if file_path not in created_files:

            graph.add_node(

                file_path,

                "FILE",

                file=chunk.get(
                    "file"
                )
            )

            created_files.add(
                file_path
            )

    # =====================================================
    # SYMBOL NODES
    # =====================================================

    for chunk in chunks:

        symbol_name = chunk.get(
            "qualified_name"
        )or chunk.get(
           "name"
        )

        if not symbol_name:

            continue

        graph.add_node(

            symbol_name,

            chunk.get(
                "type",
                "UNKNOWN"
            ),

            file=chunk.get(
                "file"
            ),

            path=chunk.get(
                "path"
            ),

            start_line=chunk.get(
                "start_line"
            ),

            end_line=chunk.get(
                "end_line"
            )
        )

    # =====================================================
    # CONTAINS EDGES
    # =====================================================

    for chunk in chunks:

        file_path = chunk.get(
            "path"
        )

        symbol_name = chunk.get(
            "qualified_name"
        )or chunk.get(
           "name"
        )

        if (

            not file_path

            or

            not symbol_name

        ):

            continue

        graph.add_edge(

            file_path,

            symbol_name,

            "CONTAINS"
        )

    # =====================================================
    # IMPORT EDGES
    # =====================================================

    from rag.repository_import_graph import (
        build_import_edges
    )

    import_edges = build_import_edges(

        chunks,

        "backend/repositories/enterprise_rag_benchmark_repo"
    )

    for edge in import_edges:

       graph.add_edge(

            edge["source"],

            edge["target"],

            edge["relationship"]
        )

    return graph