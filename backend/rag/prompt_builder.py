# =========================================================
# DETECT INTENT
# =========================================================

def detect_intent(query):

    query = query.lower()

    if "class" in query:
        return "class_search"

    elif "function" in query:
        return "function_search"

    elif "architecture" in query:
        return "architecture_question"

    elif "dependency" in query:
        return "dependency_analysis"

    elif "generate" in query:
        return "code_generation"

    elif "bug" in query:
        return "bug_fixing"

    else:
        return (
            "general_repository_question"
        )

# =========================================================
# BUILD PROMPT
# =========================================================

def build_prompt(
    query,
    intent,
    context
):

    prompt = f'''

You are an Enterprise AI Coding Assistant.

You help developers generate code
that follows the company's
engineering style and architecture.

IMPORTANT RULES:
- Follow company architecture
- Follow engineering conventions
- Use repository context carefully
- Do NOT hallucinate
- Explain clearly

==================================================
QUERY TYPE
==================================================

{intent}

==================================================
USER QUESTION
==================================================

{query}

==================================================
COMPANY REPOSITORY CONTEXT
==================================================

{context}

==================================================
FINAL RESPONSE
==================================================

'''

    return prompt