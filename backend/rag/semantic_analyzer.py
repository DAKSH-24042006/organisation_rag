
# =========================================================
# semantic_analyzer.py
# =========================================================

import ast
import re

# =========================================================
# KEYWORDS
# =========================================================

SECURITY_KEYWORDS = [

    "jwt",
    "token",
    "auth",
    "authenticate",
    "authorization",
    "login",
    "signup",
    "signin",
    "bcrypt",
    "permission",
    "session"
]

DB_KEYWORDS = [

    "sql",
    "query",
    "database",
    "mongodb",
    "postgres",
    "mysql",
    "prisma",
    "commit",
    "rollback"
]

API_KEYWORDS = [

    "request",
    "response",
    "router",
    "route",
    "endpoint",
    "axios",
    "fetch",
    "api"
]

CACHE_KEYWORDS = [

    "redis",
    "cache",
    "ttl",
    "memoize"
]

FRONTEND_KEYWORDS = [

    "useeffect",
    "usestate",
    "component",
    "props",
    "jsx",
    "tsx",
    "react"
]

SESSION_KEYWORDS = [

    "localstorage",
    "sessionstorage",
    "cookie",
    "session"
]

# =========================================================
# AST VISITOR
# =========================================================

class SemanticVisitor(ast.NodeVisitor):

    def __init__(self):

        self.imports = []

        self.calls = []

        self.conditions = []

        self.loops = []

        self.exceptions = []

        self.returns = []

    # =====================================================
    # IMPORTS
    # =====================================================

    def visit_Import(self, node):

        for alias in node.names:

            self.imports.append(
                alias.name
            )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):

        if node.module:

            self.imports.append(
                node.module
            )

        self.generic_visit(node)

    # =====================================================
    # FUNCTION CALLS
    # =====================================================

    def visit_Call(self, node):

        try:

            if isinstance(
                node.func,
                ast.Attribute
            ):

                self.calls.append(
                    node.func.attr
                )

            elif isinstance(
                node.func,
                ast.Name
            ):

                self.calls.append(
                    node.func.id
                )

        except:
            pass

        self.generic_visit(node)

    # =====================================================
    # CONDITIONS
    # =====================================================

    def visit_If(self, node):

        self.conditions.append(
            ast.dump(node.test)
        )

        self.generic_visit(node)

    # =====================================================
    # LOOPS
    # =====================================================

    def visit_For(self, node):

        self.loops.append(
            "for_loop"
        )

        self.generic_visit(node)

    def visit_While(self, node):

        self.loops.append(
            "while_loop"
        )

        self.generic_visit(node)

    # =====================================================
    # EXCEPTIONS
    # =====================================================

    def visit_Try(self, node):

        self.exceptions.append(
            "try_except"
        )

        self.generic_visit(node)

    # =====================================================
    # RETURNS
    # =====================================================

    def visit_Return(self, node):

        self.returns.append(
            "return_statement"
        )

        self.generic_visit(node)

# =========================================================
# DETECT SEMANTIC TAGS
# =========================================================

def detect_semantic_tags(code):

    semantic_tags = set()

    code_lower = code.lower()

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    if any(

        word in code_lower

        for word in SECURITY_KEYWORDS
    ):

        semantic_tags.update([

            "authentication",
            "security"
        ])

    if "jwt" in code_lower:

        semantic_tags.add("jwt")

    # =====================================================
    # DATABASE
    # =====================================================

    if any(

        word in code_lower

        for word in DB_KEYWORDS
    ):

        semantic_tags.update([

            "database",
            "data_access",
            "query_engine"
        ])

    # =====================================================
    # API
    # =====================================================

    if any(

        word in code_lower

        for word in API_KEYWORDS
    ):

        semantic_tags.update([

            "api",
            "backend",
            "request_pipeline"
        ])

    # =====================================================
    # CACHE
    # =====================================================

    if any(

        word in code_lower

        for word in CACHE_KEYWORDS
    ):

        semantic_tags.update([

            "cache",
            "performance"
        ])

    if "redis" in code_lower:

        semantic_tags.add("redis")

    # =====================================================
    # FRONTEND
    # =====================================================

    if any(

        word in code_lower

        for word in FRONTEND_KEYWORDS
    ):

        semantic_tags.update([

            "frontend",
            "ui",
            "react"
        ])

    # =====================================================
    # SESSION MANAGEMENT
    # =====================================================

    if any(

        word in code_lower

        for word in SESSION_KEYWORDS
    ):

        semantic_tags.update([

            "session_management"
        ])

    # =====================================================
    # ASYNC
    # =====================================================

    if "async" in code_lower:

        semantic_tags.add("async")

    if "await" in code_lower:

        semantic_tags.add(
            "async_workflow"
        )

    return list(semantic_tags)

# =========================================================
# BUSINESS ROLE INFERENCE
# =========================================================

def infer_business_role(tags):

    if "authentication" in tags:

        return "authentication_service"

    elif "database" in tags:

        return "database_service"

    elif "api" in tags:

        return "api_service"

    elif "cache" in tags:

        return "cache_service"

    elif "frontend" in tags:

        return "frontend_component"

    return "general_service"

# =========================================================
# GENERATE SUMMARY
# =========================================================

def generate_summary(

    tags,
    calls
):

    summary_parts = []

    # =====================================================
    # AUTH
    # =====================================================

    if "authentication" in tags:

        summary_parts.append(

            "Handles authentication and security workflows"
        )

    # =====================================================
    # DATABASE
    # =====================================================

    if "database" in tags:

        summary_parts.append(

            "Performs database operations"
        )

    # =====================================================
    # API
    # =====================================================

    if "api" in tags:

        summary_parts.append(

            "Implements API and request handling logic"
        )

    # =====================================================
    # CACHE
    # =====================================================

    if "cache" in tags:

        summary_parts.append(

            "Handles caching and performance optimization"
        )

    # =====================================================
    # FRONTEND
    # =====================================================

    if "frontend" in tags:

        summary_parts.append(

            "Implements frontend UI workflows"
        )

    # =====================================================
    # FUNCTION CALLS
    # =====================================================

    if len(calls) > 0:

        summary_parts.append(

            f"Uses functions: "
            f"{', '.join(calls[:5])}"
        )

    return ". ".join(summary_parts)

# =========================================================
# FALLBACK JS/TS CALL EXTRACTION
# =========================================================

def extract_js_calls(code):

    matches = re.findall(

        r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',

        code
    )

    ignored = {

        "if",
        "for",
        "while",
        "switch",
        "catch",
        "function"
    }

    return [

        match

        for match in matches

        if match not in ignored
    ]

# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze_code_semantics(code):

    semantic_data = {

        "semantic_tags": [],

        "business_role": "general_service",

        "summary": "",

        "imports": [],

        "calls": [],

        "conditions": [],

        "loops": [],

        "exceptions": [],

        "returns": []
    }

    # =====================================================
    # SEMANTIC TAGS
    # =====================================================

    tags = detect_semantic_tags(code)

    role = infer_business_role(tags)

    # =====================================================
    # PYTHON AST ANALYSIS
    # =====================================================

    try:

        tree = ast.parse(code)

        visitor = SemanticVisitor()

        visitor.visit(tree)

        calls = visitor.calls

        summary = generate_summary(
            tags,
            calls
        )

        semantic_data.update({

            "semantic_tags": tags,

            "business_role": role,

            "summary": summary,

            "imports": visitor.imports,

            "calls": calls,

            "conditions": visitor.conditions,

            "loops": visitor.loops,

            "exceptions": visitor.exceptions,

            "returns": visitor.returns
        })

    # =====================================================
    # JS/TS/React FALLBACK
    # =====================================================

    except Exception:

        js_calls = extract_js_calls(
            code
        )

        summary = generate_summary(
            tags,
            js_calls
        )

        semantic_data.update({

            "semantic_tags": tags,

            "business_role": role,

            "summary": summary,

            "calls": js_calls
        })

    return semantic_data

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_code = '''

import jwt

def login_user(token):

    if token:

        return jwt.decode(token)

'''

    result = analyze_code_semantics(
        sample_code
    )

    print(result)
