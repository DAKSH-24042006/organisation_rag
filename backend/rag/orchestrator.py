from rag.retriever import (
    retrieve,
    compress_context
)

from rag.prompt_builder import (
    detect_intent,
    build_prompt
)

from rag.llm_engine import (
    generate_llm_response
)

# =========================================================
# MAIN ORCHESTRATOR
# =========================================================

def orchestrate_query(query):

    print("\nDetecting query intent...\n")

    intent = detect_intent(query)

    print(f"Intent: {intent}")

    print("\nRetrieving chunks...\n")

    retrieved_chunks = retrieve(query)

    print(
        f"Retrieved "
        f"{len(retrieved_chunks)} chunks"
    )

    context = compress_context(
        retrieved_chunks
    )

    prompt = build_prompt(
        query,
        intent,
        context
    )

    final_response = generate_llm_response(
        prompt
    )

    return final_response