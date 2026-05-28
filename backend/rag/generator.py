# =========================================================
# generator.py
# =========================================================

import json

from rag.retriever import (
    retrieve_relevant_code
)

from rag.prompt_builder import (
    build_system_prompt,
    build_generation_prompt
)

# =========================================================
# OPTIONAL OPENAI
# =========================================================

# pip install openai

from openai import OpenAI

# =========================================================
# CONFIG
# =========================================================

MODEL_NAME = "gpt-4.1-mini"

MAX_CONTEXT_CHUNKS = 5

TEMPERATURE = 0.2

# =========================================================
# OPENAI CLIENT
# =========================================================

client = OpenAI()

# =========================================================
# CLEAN CONTEXT
# =========================================================

def clean_context(context):

    context = context.strip()

    return context

# =========================================================
# LIMIT CHUNKS
# =========================================================

def limit_chunks(

    retrieved_chunks,
    max_chunks=MAX_CONTEXT_CHUNKS
):

    unique_chunks = []

    seen = set()

    for chunk in retrieved_chunks:

        identifier = (

            chunk["name"]
            + chunk["path"]
        )

        if identifier not in seen:

            seen.add(identifier)

            unique_chunks.append(chunk)

    return unique_chunks[:max_chunks]

# =========================================================
# BUILD CONTEXT
# =========================================================

def build_context(

    retrieved_chunks
):

    context = ""

    for chunk in retrieved_chunks:

        chunk_context = f"""

==================================================
FILE:
{chunk['file']}

FUNCTION / CLASS:
{chunk['name']}

BUSINESS ROLE:
{chunk['business_role']}

SEMANTIC TAGS:
{' '.join(chunk['semantic_tags'])}

SUMMARY:
{chunk['summary']}

IMPORTS:
{' '.join(chunk['imports'])}

DEPENDENCIES:
{' '.join(chunk['dependencies'])}

CODE:
{chunk['content']}
==================================================

"""

        context += chunk_context

    return clean_context(context)

# =========================================================
# GENERATE CODE
# =========================================================

def generate_code(

    user_query
):

    print("\n" + "=" * 80)

    print("UNDERSTANDING USER QUERY")

    print("=" * 80)

    # =====================================================
    # RETRIEVE RELEVANT CODE
    # =====================================================

    retrieval_results = retrieve_relevant_code(

        user_query=user_query,

        top_k=10
    )

    retrieved_chunks = retrieval_results[
        "retrieved_chunks"
    ]

    # =====================================================
    # LIMIT CHUNKS
    # =====================================================

    retrieved_chunks = limit_chunks(

        retrieved_chunks
    )

    print(
        f"\nRetrieved Chunks: "
        f"{len(retrieved_chunks)}"
    )

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context = build_context(

        retrieved_chunks
    )

    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    system_prompt = build_system_prompt()

    # =====================================================
    # USER PROMPT
    # =====================================================

    user_prompt = build_generation_prompt(

        user_query=user_query,

        retrieved_context=context
    )

    print("\n" + "=" * 80)

    print("GENERATING COMPANY-AWARE CODE")

    print("=" * 80)

    # =====================================================
    # OPENAI CALL
    # =====================================================

    response = client.chat.completions.create(

        model=MODEL_NAME,

        temperature=TEMPERATURE,

        messages=[

            {
                "role": "system",

                "content": system_prompt
            },

            {
                "role": "user",

                "content": user_prompt
            }
        ]
    )

    generated_code = response.choices[
        0
    ].message.content

    return {

        "query": user_query,

        "retrieved_chunks":
        retrieved_chunks,

        "context":
        context,

        "generated_code":
        generated_code
    }

# =========================================================
# SAVE OUTPUT
# =========================================================

def save_output(

    generated_code,
    output_path="generated_output.txt"
):

    with open(

        output_path,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(generated_code)

    print(
        f"\nGenerated code saved to: "
        f"{output_path}"
    )

# =========================================================
# DISPLAY RETRIEVAL RESULTS
# =========================================================

def display_retrieved_chunks(

    retrieved_chunks
):

    print("\n" + "=" * 80)

    print("RETRIEVED CHUNKS")

    print("=" * 80)

    for idx, chunk in enumerate(

        retrieved_chunks
    ):

        print(f"\nCHUNK {idx + 1}")

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
            f"Final Score: "
            f"{chunk.get('final_score', 0)}"
        )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 80)

    print("COMPANY-AWARE CODE GENERATION SYSTEM")

    print("=" * 80)

    user_query = input(

        "\nEnter your coding request:\n\n"
    )

    results = generate_code(

        user_query
    )

    display_retrieved_chunks(

        results[
            "retrieved_chunks"
        ]
    )

    print("\n" + "=" * 80)

    print("GENERATED CODE")

    print("=" * 80)

    print(

        results[
            "generated_code"
        ]
    )

    save_output(

        results[
            "generated_code"
        ]
    )