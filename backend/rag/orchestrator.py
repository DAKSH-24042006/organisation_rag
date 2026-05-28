# =========================================================
# orchestrator.py
# =========================================================

from rag.retriever import (
    retrieve_relevant_code
)

from rag.context_builder import (
    build_final_context
)

from rag.prompt_builder import (

    build_system_prompt,

    build_generation_prompt
)

from rag.llm_engine import (
    generate_llm_response
)

# =========================================================
# CONFIG
# =========================================================

TOP_K_RETRIEVAL = 10

# =========================================================
# DISPLAY QUERY INFO
# =========================================================

def display_query_info(

    query_data
):

    print("\n" + "=" * 80)

    print("QUERY UNDERSTANDING")

    print("=" * 80)

    print(

        f"\nSemantic Tags: "

        f"{query_data['semantic_tags']}"
    )

    print(

        f"\nBusiness Roles: "

        f"{query_data['business_roles']}"
    )

    print(

        f"\nArchitecture: "

        f"{query_data['architecture']}"
    )

# =========================================================
# DISPLAY RETRIEVAL RESULTS
# =========================================================

def display_retrieval_results(

    retrieved_chunks
):

    print("\n" + "=" * 80)

    print("RETRIEVED CHUNKS")

    print("=" * 80)

    for idx, chunk in enumerate(

        retrieved_chunks[:5]
    ):

        print(f"\nRESULT {idx + 1}")

        print(
            f"Name: {chunk['name']}"
        )

        print(
            f"File: {chunk['file']}"
        )

        print(
            f"Business Role: "
            f"{chunk['business_role']}"
        )

        print(
            f"Semantic Tags: "
            f"{chunk['semantic_tags']}"
        )

        print(
            f"Summary: "
            f"{chunk['summary']}"
        )

        print(
            f"Score: "
            f"{chunk.get('final_score', 0)}"
        )

# =========================================================
# GENERATE FINAL RESPONSE
# =========================================================

def generate_repository_aware_response(

    user_query
):

    print("\n" + "=" * 80)

    print("ENTERPRISE AI CODING SYSTEM")

    print("=" * 80)

    # =====================================================
    # RETRIEVAL
    # =====================================================

    retrieval_results = retrieve_relevant_code(

        user_query=user_query,

        top_k=TOP_K_RETRIEVAL
    )

    query_data = retrieval_results[
        "query_data"
    ]

    retrieved_chunks = retrieval_results[
        "retrieved_chunks"
    ]

    # =====================================================
    # DISPLAY QUERY INFO
    # =====================================================

    display_query_info(
        query_data
    )

    # =====================================================
    # DISPLAY RETRIEVAL RESULTS
    # =====================================================

    display_retrieval_results(
        retrieved_chunks
    )

    # =====================================================
    # CONTEXT BUILDING
    # =====================================================

    print("\n" + "=" * 80)

    print("BUILDING CONTEXT")

    print("=" * 80)

    final_context = build_final_context(

        retrieved_chunks
    )

    # =====================================================
    # PROMPT BUILDING
    # =====================================================

    print("\n" + "=" * 80)

    print("BUILDING PROMPTS")

    print("=" * 80)

    system_prompt = build_system_prompt()

    generation_prompt = (

        build_generation_prompt(

            user_query=user_query,

            retrieved_context=final_context
        )
    )

    # =====================================================
    # LLM GENERATION
    # =====================================================

    print("\n" + "=" * 80)

    print("GENERATING RESPONSE")

    print("=" * 80)

    generated_response = generate_llm_response(

        prompt=generation_prompt,

        system_prompt=system_prompt
    )

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    return {

        "query":
        user_query,

        "query_data":
        query_data,

        "retrieved_chunks":
        retrieved_chunks,

        "final_context":
        final_context,

        "system_prompt":
        system_prompt,

        "generation_prompt":
        generation_prompt,

        "generated_response":
        generated_response
    }

# =========================================================
# SAVE OUTPUT
# =========================================================

def save_output(

    generated_response,
    output_file="generated_output.txt"
):

    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(generated_response)

    print(

        f"\nOutput saved to: "
        f"{output_file}"
    )

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline(query):

    results = generate_repository_aware_response(
        query
    )

    save_output(

        results[
            "generated_response"
        ]
    )

    return results

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 80)

    print("COMPANY-AWARE AI CODING SYSTEM")

    print("=" * 80)

    user_query = input(

        "\nEnter your coding request:\n\n"
    )

    results = run_pipeline(
        user_query
    )

    print("\n" + "=" * 80)

    print("FINAL GENERATED RESPONSE")

    print("=" * 80)

    print(

        results[
            "generated_response"
        ]
    )