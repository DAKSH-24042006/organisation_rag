from rag.retriever import retrieve

# =========================================================
# CONTEXT COMPRESSION
# =========================================================

def compress_context(results):

    context_blocks = []

    for result in results:

        payload = result["payload"]

        context_blocks.append(f'''

Repository:
{payload['repo_name']}

File:
{payload['file']}

Type:
{payload['type']}

Name:
{payload['name']}

Code:
{payload['content']}
''')

    return "\n".join(
        context_blocks
    )

# =========================================================
# PROMPT BUILDER
# =========================================================

def build_prompt(

    query,
    context
):

    return f'''

You are an enterprise AI coding assistant.

Use the repository context below
for repository-aware generation.

Repository Context:

{context}

User Request:

{query}

Generate production-quality code
following repository conventions.
'''

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline(query):

    retrieved_results = retrieve(
        query
    )

    compressed_context = compress_context(
        retrieved_results
    )

    prompt = build_prompt(

        query,
        compressed_context
    )

    return {

        "results":
        retrieved_results,

        "context":
        compressed_context,

        "prompt":
        prompt
    }