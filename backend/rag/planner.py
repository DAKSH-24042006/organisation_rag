# =========================================================
# planner.py
# =========================================================

# =========================================================
# DETECT TASK TYPE
# =========================================================

def detect_task_type(query):

    query = query.lower()

    if any(

        word in query

        for word in [

            "generate",
            "create",
            "implement",
            "build"
        ]
    ):

        return "code_generation"

    elif any(

        word in query

        for word in [

            "fix",
            "bug",
            "debug",
            "error"
        ]
    ):

        return "bug_fixing"

    elif any(

        word in query

        for word in [

            "optimize",
            "improve",
            "performance"
        ]
    ):

        return "optimization"

    return "general"

# =========================================================
# BUILD RETRIEVAL PLAN
# =========================================================

def build_retrieval_plan(query):

    query = query.lower()

    plan = {

        "required_roles": [],

        "required_tags": [],

        "required_workflows": []
    }

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    if any(

        word in query

        for word in [

            "jwt",
            "auth",
            "authentication",
            "token"
        ]
    ):

        plan["required_roles"].extend([

            "authentication_service",
            "api_service"
        ])

        plan["required_tags"].extend([

            "authentication",
            "security",
            "jwt"
        ])

        plan["required_workflows"].append(
            "authentication_flow"
        )

    # =====================================================
    # DATABASE
    # =====================================================

    if any(

        word in query

        for word in [

            "database",
            "sql",
            "query"
        ]
    ):

        plan["required_roles"].append(
            "database_service"
        )

        plan["required_tags"].append(
            "database"
        )

    # =====================================================
    # CACHE
    # =====================================================

    if any(

        word in query

        for word in [

            "redis",
            "cache"
        ]
    ):

        plan["required_roles"].append(
            "cache_service"
        )

        plan["required_tags"].append(
            "cache"
        )

    return plan

# =========================================================
# GENERATE EXECUTION PLAN
# =========================================================

def generate_execution_plan(query):

    task_type = detect_task_type(query)

    retrieval_plan = build_retrieval_plan(
        query
    )

    return {

        "task_type":
        task_type,

        "retrieval_plan":
        retrieval_plan
    }

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    query = (

        "Create JWT middleware "
        "with Redis caching"
    )

    plan = generate_execution_plan(
        query
    )

    print(plan)