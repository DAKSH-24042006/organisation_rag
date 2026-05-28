# =========================================================
# agent.py
# =========================================================

from rag.orchestrator import (
    run_pipeline
)

from rag.knowledge_graph import (

    build_knowledge_graph,

    get_semantic_relationships
)

from rag.workflow_engine import (

    build_workflow_chains,

    build_workflow_context
)

from rag.reranker import (
    rerank_results
)

# =========================================================
# AGENT MEMORY
# =========================================================

agent_memory = []

# =========================================================
# ANALYZE RETRIEVAL GAPS
# =========================================================

def analyze_retrieval_gaps(results):

    retrieved_chunks = results[
        "retrieved_chunks"
    ]

    if len(retrieved_chunks) < 3:

        return True

    return False

# =========================================================
# ENHANCE CONTEXT USING GRAPH
# =========================================================

def enhance_with_knowledge_graph(

    retrieved_chunks
):

    enhanced_chunks = retrieved_chunks.copy()

    for chunk in retrieved_chunks:

        relationships = (

            get_semantic_relationships(

                chunk.get("name")
            )
        )

        for relation in relationships[:2]:

            enhanced_chunks.append({

                "name":
                relation["target"],

                "summary":
                f"Related via tags: "
                f"{relation['shared_tags']}",

                "semantic_tags":
                relation["shared_tags"],

                "business_role":
                "related_service",

                "calls":
                [],

                "file":
                "graph_relation",

                "content":
                ""
            })

    return enhanced_chunks

# =========================================================
# AGENT EXECUTION
# =========================================================

def run_agent(user_query):

    print("\n" + "=" * 80)

    print("ENTERPRISE AI AGENT")

    print("=" * 80)

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    build_knowledge_graph()

    # =====================================================
    # INITIAL PIPELINE
    # =====================================================

    results = run_pipeline(
        user_query
    )

    # =====================================================
    # GAP ANALYSIS
    # =====================================================

    needs_more_context = (

        analyze_retrieval_gaps(
            results
        )
    )

    # =====================================================
    # RERANK
    # =====================================================

    reranked_chunks = rerank_results(

        results["retrieved_chunks"],

        results["query_data"]
    )

    # =====================================================
    # GRAPH ENHANCEMENT
    # =====================================================

    enhanced_chunks = (

        enhance_with_knowledge_graph(
            reranked_chunks
        )
    )

    # =====================================================
    # WORKFLOW ENGINE
    # =====================================================

    workflows = build_workflow_chains(

        enhanced_chunks
    )

    workflow_context = (

        build_workflow_context(
            workflows
        )
    )

    # =====================================================
    # MEMORY
    # =====================================================

    agent_memory.append({

        "query":
        user_query,

        "workflow_context":
        workflow_context
    })

    return {

        "results":
        results,

        "reranked_chunks":
        reranked_chunks,

        "enhanced_chunks":
        enhanced_chunks,

        "workflow_context":
        workflow_context,

        "needs_more_context":
        needs_more_context
    }

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    query = input(

        "\nEnter Agent Query:\n\n"
    )

    output = run_agent(query)

    print("\n" + "=" * 80)

    print("WORKFLOW CONTEXT")

    print("=" * 80)

    print(

        output[
            "workflow_context"
        ]
    )