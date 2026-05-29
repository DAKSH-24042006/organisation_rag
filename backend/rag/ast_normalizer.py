# =========================================================
# UNIVERSAL AST NORMALIZER
# =========================================================

"""
Converts language-specific Tree-Sitter node types into
universal symbol categories.

Example:

Python:
    function_definition

Java:
    method_declaration

Go:
    function_declaration

Rust:
    function_item

ALL become:

    FUNCTION
"""

# =========================================================
# UNIVERSAL NODE GROUPS
# =========================================================

NODE_GROUPS = {

    "FUNCTION": {

        "function_definition",
        "function_declaration",
        "method_definition",
        "method_declaration",
        "function_item",
        "constructor_declaration"
    },

    "CLASS": {

        "class_definition",
        "class_declaration",
        "class_body"
    },

    "INTERFACE": {

        "interface_declaration"
    },

    "STRUCT": {

        "struct_item",
        "struct_specifier"
    },

    "ENUM": {

        "enum_declaration",
        "enum_specifier"
    },

    "MODULE": {

        "module",
        "module_declaration",
        "package_clause"
    },

    "NAMESPACE": {

        "namespace_definition"
    },

    "IMPORT": {

        "import_statement",
        "import_from_statement",
        "namespace_import",
        "using_directive",
        "using_declaration"
    },

    "CALL": {

        "call",
        "call_expression",
        "method_invocation",
        "function_call"
    },

    "VARIABLE": {

        "assignment",
        "variable_declarator",
        "local_variable_declaration"
    },

    "CONSTANT": {

        "const_item",
        "constant_declaration"
    },

    "COMMENT": {

        "comment"
    }
}

# =========================================================
# REVERSE LOOKUP
# =========================================================

NODE_TYPE_MAP = {}

for category, node_types in NODE_GROUPS.items():

    for node_type in node_types:

        NODE_TYPE_MAP[node_type] = category

# =========================================================
# NORMALIZE NODE TYPE
# =========================================================

def normalize_node_type(node_type):

    return NODE_TYPE_MAP.get(
        node_type,
        "OTHER"
    )

# =========================================================
# CHECK CATEGORY
# =========================================================

def is_symbol_node(node_type):

    return normalize_node_type(
        node_type
    ) != "OTHER"

# =========================================================
# CATEGORY HELPERS
# =========================================================

def is_function(node_type):

    return normalize_node_type(
        node_type
    ) == "FUNCTION"

def is_class(node_type):

    return normalize_node_type(
        node_type
    ) == "CLASS"

def is_import(node_type):

    return normalize_node_type(
        node_type
    ) == "IMPORT"

def is_call(node_type):

    return normalize_node_type(
        node_type
    ) == "CALL"

def is_interface(node_type):

    return normalize_node_type(
        node_type
    ) == "INTERFACE"

def is_struct(node_type):

    return normalize_node_type(
        node_type
    ) == "STRUCT"

def is_module(node_type):

    return normalize_node_type(
        node_type
    ) == "MODULE"

# =========================================================
# UNIVERSAL SYMBOL TYPES
# =========================================================

SUPPORTED_SYMBOL_TYPES = [

    "FUNCTION",
    "CLASS",
    "INTERFACE",
    "STRUCT",
    "ENUM",
    "MODULE",
    "NAMESPACE",
    "IMPORT",
    "CALL",
    "VARIABLE",
    "CONSTANT"
]