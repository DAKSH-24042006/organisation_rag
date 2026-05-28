# =========================================================
# context_builder.py
# =========================================================

from collections import defaultdict

# =========================================================
# CONFIG
# =========================================================

MAX_TOTAL_CHUNKS = 8

MAX_CODE_LENGTH = 3000

# =========================================================
# CLEAN CODE
# =========================================================

def clean_code(code):

    if not code:
        return ""

    code = code.strip()

    return code[:MAX_CODE_LENGTH]

# =========================================================
# DEDUPLICATE CHUNKS
# =========================================================

def deduplicate_chunks(chunks):

    unique_chunks = []

    seen = set()

    for chunk in chunks:

        identifier = (

            chunk.get("name", "")
            +
            chunk.get("path", "")
        )

        if identifier not in seen:

            seen.add(identifier)

            unique_chunks.append(chunk)

    return unique_chunks

# =========================================================
# SCORE CHUNKS
# =========================================================

def score_chunk(chunk):

    score = 0

    # =====================================================
    # FINAL RETRIEVAL SCORE
    # =====================================================

    score += chunk.get(
        "final_score",
        0
    )

    # =====================================================
    # IMPORTANT BUSINESS ROLES
    # =====================================================

    important_roles = [

        "authentication_service",
        "api_service",
        "database_service",
        "cache_service"
    ]

    if (

        chunk.get(
            "business_role"
        )

        in

        important_roles
    ):

        score += 1.5

    # =====================================================
    # SEMANTIC TAG BONUS
    # =====================================================

    score += len(

        chunk.get(
            "semantic_tags",
            []
        )

    ) * 0.1

    # =====================================================
    # FUNCTION CALL BONUS
    # =====================================================

    score += len(

        chunk.get(
            "calls",
            []
        )

    ) * 0.05

    return score

# =========================================================
# SORT CHUNKS
# =========================================================

def sort_chunks(chunks):

    sorted_chunks = sorted(

        chunks,

        key=lambda x: score_chunk(x),

        reverse=True
    )

    return sorted_chunks

# =========================================================
# GROUP BY BUSINESS ROLE
# =========================================================

def group_by_business_role(chunks):

    grouped = defaultdict(list)

    for chunk in chunks:

        role = chunk.get(

            "business_role",

            "general_service"
        )

        grouped[role].append(chunk)

    return grouped

# =========================================================
# BUILD ARCHITECTURE SECTION
# =========================================================

def build_architecture_section(grouped_chunks):

    architecture_context = ""

    architecture_context += """

==================================================
ARCHITECTURE PATTERNS
==================================================

"""

    for role, chunks in grouped_chunks.items():

        architecture_context += f"""

--------------------------------------------------
BUSINESS ROLE:
{role}
--------------------------------------------------

"""

        for chunk in chunks[:2]:

            architecture_context += f"""

FILE:
{chunk.get('file')}

NAME:
{chunk.get('name')}

SUMMARY:
{chunk.get('summary')}

SEMANTIC TAGS:
{' '.join(chunk.get('semantic_tags', []))}

"""

    return architecture_context

# =========================================================
# BUILD WORKFLOW SECTION
# =========================================================

def build_workflow_section(chunks):

    workflow_context = """

==================================================
WORKFLOW PATTERNS
==================================================

"""

    for chunk in chunks[:5]:

        workflow_context += f"""

--------------------------------------------------
WORKFLOW COMPONENT
--------------------------------------------------

NAME:
{chunk.get('name')}

BUSINESS ROLE:
{chunk.get('business_role')}

FUNCTION CALLS:
{' '.join(chunk.get('calls', []))}

CONDITIONS:
{len(chunk.get('conditions', []))}

LOOPS:
{len(chunk.get('loops', []))}

EXCEPTIONS:
{len(chunk.get('exceptions', []))}

SUMMARY:
{chunk.get('summary')}

"""

    return workflow_context

# =========================================================
# BUILD UTILITY SECTION
# =========================================================

def build_utility_section(chunks):

    utility_context = """

==================================================
UTILITY REUSE PATTERNS
==================================================

"""

    utilities_found = set()

    for chunk in chunks:

        calls = chunk.get(
            "calls",
            []
        )

        for call in calls[:10]:

            if call not in utilities_found:

                utilities_found.add(call)

                utility_context += f"""

- {call}

"""

    return utility_context

# =========================================================
# BUILD CODE EXAMPLES SECTION
# =========================================================

def build_code_examples_section(chunks):

    code_context = """

==================================================
IMPORTANT CODE EXAMPLES
==================================================

"""

    for chunk in chunks[:MAX_TOTAL_CHUNKS]:

        code_context += f"""

==================================================
FILE:
{chunk.get('file')}

NAME:
{chunk.get('name')}

BUSINESS ROLE:
{chunk.get('business_role')}

SEMANTIC TAGS:
{' '.join(chunk.get('semantic_tags', []))}

SUMMARY:
{chunk.get('summary')}

CODE:
{clean_code(chunk.get('content', ''))}

==================================================

"""

    return code_context

# =========================================================
# BUILD DEPENDENCY SECTION
# =========================================================

def build_dependency_section(chunks):

    dependency_context = """

==================================================
DEPENDENCY PATTERNS
==================================================

"""

    dependencies = set()

    imports = set()

    for chunk in chunks:

        for dep in chunk.get(
            "dependencies",
            []
        ):

            dependencies.add(dep)

        for imp in chunk.get(
            "imports",
            []
        ):

            imports.add(imp)

    dependency_context += """

--------------------------------------------------
DEPENDENCIES
--------------------------------------------------

"""

    for dep in sorted(dependencies):

        dependency_context += f"- {dep}\n"

    dependency_context += """

--------------------------------------------------
IMPORTS
--------------------------------------------------

"""

    for imp in sorted(imports):

        dependency_context += f"- {imp}\n"

    return dependency_context

# =========================================================
# BUILD FINAL CONTEXT
# =========================================================

def build_final_context(

    retrieved_chunks
):

    # =====================================================
    # DEDUPLICATION
    # =====================================================

    retrieved_chunks = deduplicate_chunks(

        retrieved_chunks
    )

    # =====================================================
    # SORTING
    # =====================================================

    retrieved_chunks = sort_chunks(

        retrieved_chunks
    )

    # =====================================================
    # LIMIT
    # =====================================================

    retrieved_chunks = retrieved_chunks[
        :MAX_TOTAL_CHUNKS
    ]

    # =====================================================
    # GROUPING
    # =====================================================

    grouped_chunks = group_by_business_role(

        retrieved_chunks
    )

    # =====================================================
    # BUILD SECTIONS
    # =====================================================

    architecture_section = (

        build_architecture_section(
            grouped_chunks
        )
    )

    workflow_section = (

        build_workflow_section(
            retrieved_chunks
        )
    )

    utility_section = (

        build_utility_section(
            retrieved_chunks
        )
    )

    dependency_section = (

        build_dependency_section(
            retrieved_chunks
        )
    )

    code_examples_section = (

        build_code_examples_section(
            retrieved_chunks
        )
    )

    # =====================================================
    # FINAL CONTEXT
    # =====================================================

    final_context = f"""

{architecture_section}

{workflow_section}

{utility_section}

{dependency_section}

{code_examples_section}

"""

    return final_context

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_chunks = [

        {

            "file":
            "auth.py",

            "name":
            "verify_token",

            "business_role":
            "authentication_service",

            "semantic_tags":
            [
                "authentication",
                "jwt",
                "security"
            ],

            "summary":
            "Validates JWT tokens.",

            "calls":
            [
                "jwt.decode",
                "redis.get"
            ],

            "conditions":
            [
                "token_expired"
            ],

            "loops":
            [],

            "exceptions":
            [
                "try_except"
            ],

            "dependencies":
            [
                "jwt",
                "redis"
            ],

            "imports":
            [
                "jwt",
                "redis"
            ],

            "content":
            "def verify_token(): pass",

            "final_score":
            2.5
        }
    ]

    context = build_final_context(
        sample_chunks
    )

    print("\n" + "=" * 80)

    print("FINAL CONTEXT")

    print("=" * 80)

    print(context)