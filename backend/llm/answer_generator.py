import ollama
from rag.config import OLLAMA_MODEL


def generate_answer(query, context):
    from rag.retriever import classify_query
    qtype = classify_query(query)
    
    if qtype == "FILE_RECOVERY":
        prompt = f"""You are a software repository assistant.
The user is requesting the full code of a file.

Below is the retrieved full content of the file. Please present the complete, uninterrupted code inside a single Markdown code block, with correct syntax highlighting. Do not explain, truncate, summarize, or omit any parts of the code.

File Content:
{context}

Answer:
"""
    else:
        prompt = f"""You are a software repository assistant.

Answer ONLY using the retrieved repository context. Provide a clear, detailed, and structured explanation.

If the answer is not available in the context, say so clearly.

Question:
{query}

Retrieved Context:
{context}

Answer:
"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]