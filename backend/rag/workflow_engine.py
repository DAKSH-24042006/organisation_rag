# =========================================================
# workflow_engine.py
# =========================================================

from collections import defaultdict

# =========================================================
# BUILD WORKFLOW CHAINS
# =========================================================

def build_workflow_chains(chunks):

    workflows = defaultdict(list)

    for chunk in chunks:

        role = chunk.get(
            "business_role",
            "general_service"
        )

        workflows[role].append({

            "name":
            chunk.get("name"),

            "calls":
            chunk.get("calls", []),

            "summary":
            chunk.get("summary"),

            "file":
            chunk.get("file")
        })

    return workflows

# =========================================================
# GET AUTH WORKFLOW
# =========================================================

def get_authentication_workflow(workflows):

    auth_flow = workflows.get(
        "authentication_service",
        []
    )

    return auth_flow

# =========================================================
# GET API WORKFLOW
# =========================================================

def get_api_workflow(workflows):

    api_flow = workflows.get(
        "api_service",
        []
    )

    return api_flow

# =========================================================
# GET DATABASE WORKFLOW
# =========================================================

def get_database_workflow(workflows):

    db_flow = workflows.get(
        "database_service",
        []
    )

    return db_flow

# =========================================================
# BUILD WORKFLOW CONTEXT
# =========================================================

def build_workflow_context(workflows):

    context = ""

    for role, components in workflows.items():

        context += f"""

==================================================
WORKFLOW:
{role}
==================================================

"""

        for component in components:

            context += f"""

NAME:
{component['name']}

FILE:
{component['file']}

SUMMARY:
{component['summary']}

CALLS:
{' '.join(component['calls'])}

"""

    return context

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_chunks = [

        {

            "name":
            "verify_token",

            "business_role":
            "authentication_service",

            "calls":
            [
                "jwt.decode",
                "redis.get"
            ],

            "summary":
            "Verifies JWT token.",

            "file":
            "auth.py"
        }
    ]

    workflows = build_workflow_chains(
        sample_chunks
    )

    context = build_workflow_context(
        workflows
    )

    print(context)