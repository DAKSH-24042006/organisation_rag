# =========================================================
# prompt_builder.py
# =========================================================

# =========================================================
# DETECT INTENT
# =========================================================

def detect_intent(query):

    query = query.lower()

    # =====================================================
    # CODE GENERATION
    # =====================================================

    generation_keywords = [

        "generate",
        "create",
        "build",
        "implement",
        "write",
        "develop"
    ]

    # =====================================================
    # BUG FIXING
    # =====================================================

    bug_keywords = [

        "bug",
        "fix",
        "error",
        "issue",
        "debug",
        "crash"
    ]

    # =====================================================
    # ARCHITECTURE
    # =====================================================

    architecture_keywords = [

        "architecture",
        "design",
        "structure",
        "workflow",
        "system"
    ]

    # =====================================================
    # DEPENDENCIES
    # =====================================================

    dependency_keywords = [

        "dependency",
        "dependencies",
        "package",
        "library",
        "framework"
    ]

    # =====================================================
    # CLASS SEARCH
    # =====================================================

    class_keywords = [

        "class",
        "model",
        "service",
        "manager"
    ]

    # =====================================================
    # FUNCTION SEARCH
    # =====================================================

    function_keywords = [

        "function",
        "method",
        "utility",
        "helper"
    ]

    # =====================================================
    # GENERATION
    # =====================================================

    if any(

        word in query

        for word in generation_keywords
    ):

        return "code_generation"

    # =====================================================
    # BUG FIXING
    # =====================================================

    elif any(

        word in query

        for word in bug_keywords
    ):

        return "bug_fixing"

    # =====================================================
    # ARCHITECTURE
    # =====================================================

    elif any(

        word in query

        for word in architecture_keywords
    ):

        return "architecture_question"

    # =====================================================
    # DEPENDENCIES
    # =====================================================

    elif any(

        word in query

        for word in dependency_keywords
    ):

        return "dependency_analysis"

    # =====================================================
    # CLASS SEARCH
    # =====================================================

    elif any(

        word in query

        for word in class_keywords
    ):

        return "class_search"

    # =====================================================
    # FUNCTION SEARCH
    # =====================================================

    elif any(

        word in query

        for word in function_keywords
    ):

        return "function_search"

    # =====================================================
    # DEFAULT
    # =====================================================

    return "general_repository_question"

# =========================================================
# BUILD SYSTEM PROMPT
# =========================================================

def build_system_prompt():

    system_prompt = """

You are an Enterprise Company-Aware AI Coding Assistant.

You are connected to a semantic repository
retrieval system that provides:

- company architecture
- coding conventions
- reusable utilities
- workflow patterns
- framework standards
- semantic code understanding

Your job is to generate high-quality,
production-ready code that follows the
existing engineering ecosystem.

==================================================
IMPORTANT ENGINEERING RULES
==================================================

1. Follow existing repository architecture.

2. Reuse existing patterns whenever possible.

3. Reuse internal utilities and helpers.

4. Follow naming conventions strictly.

5. Do NOT introduce unnecessary abstractions.

6. Maintain consistency with retrieved code.

7. Keep generated code modular and readable.

8. Follow framework best practices.

9. Avoid hallucinating APIs or utilities.

10. Prefer extending existing patterns over
creating completely new implementations.

==================================================
CODE GENERATION RULES
==================================================

- Generate production-ready code.
- Include proper error handling.
- Follow semantic intent from retrieved code.
- Preserve architectural consistency.
- Keep imports clean and minimal.
- Reuse retrieved implementation styles.
- Follow dependency usage patterns.

==================================================
RESPONSE RULES
==================================================

- Explain important engineering decisions.
- Clearly separate explanation and code.
- Do not generate unnecessary files.
- Avoid placeholder implementations.
- Keep output deterministic and clean.

"""

    return system_prompt

# =========================================================
# BUILD CONTEXT SECTION
# =========================================================

def build_context_section(

    retrieved_context
):

    context_section = f"""

==================================================
COMPANY REPOSITORY CONTEXT
==================================================

The following context was retrieved from the
company repositories using semantic hybrid
retrieval.

Use this information carefully to understand:

- architecture
- workflows
- utilities
- coding conventions
- implementation patterns
- dependency usage
- engineering style

REPOSITORY CONTEXT:

{retrieved_context}

"""

    return context_section

# =========================================================
# BUILD QUERY SECTION
# =========================================================

def build_query_section(

    user_query,
    intent
):

    query_section = f"""

==================================================
USER REQUEST
==================================================

Request Type:
{intent}

Developer Request:
{user_query}

"""

    return query_section

# =========================================================
# BUILD GENERATION INSTRUCTIONS
# =========================================================

def build_generation_instructions():

    instructions = """

==================================================
FINAL GENERATION TASK
==================================================

Generate the best possible implementation
for the user's request.

Requirements:

- Follow repository architecture.
- Follow retrieved patterns.
- Reuse existing conventions.
- Maintain semantic consistency.
- Keep implementation production-ready.
- Include clear explanations when needed.
- Prefer maintainability and readability.
- Keep logic modular.
- Avoid unnecessary complexity.

Return:

1. Explanation
2. Complete Code
3. Important Notes

"""

    return instructions

# =========================================================
# BUILD FINAL GENERATION PROMPT
# =========================================================

def build_generation_prompt(

    user_query,
    retrieved_context
):

    # =====================================================
    # DETECT INTENT
    # =====================================================

    intent = detect_intent(
        user_query
    )

    # =====================================================
    # QUERY SECTION
    # =====================================================

    query_section = build_query_section(

        user_query=user_query,

        intent=intent
    )

    # =====================================================
    # CONTEXT SECTION
    # =====================================================

    context_section = build_context_section(

        retrieved_context
    )

    # =====================================================
    # FINAL INSTRUCTIONS
    # =====================================================

    generation_instructions = (

        build_generation_instructions()
    )

    # =====================================================
    # FINAL PROMPT
    # =====================================================

    final_prompt = f"""

{query_section}

{context_section}

{generation_instructions}

"""

    return final_prompt

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_query = (

        "Create JWT authentication middleware "
        "with refresh token support"
    )

    sample_context = """

FastAPI middleware example using JWT.

Authentication utility using Redis session storage.

Token validation workflow with expiration handling.

"""

    prompt = build_generation_prompt(

        user_query=sample_query,

        retrieved_context=sample_context
    )

    print("\n" + "=" * 80)

    print("SYSTEM PROMPT")

    print("=" * 80)

    print(

        build_system_prompt()
    )

    print("\n" + "=" * 80)

    print("FINAL GENERATION PROMPT")

    print("=" * 80)

    print(prompt)