# =========================================================
# UNIVERSAL AST NORMALIZER
# =========================================================

"""
Converts language-specific Tree-Sitter node types into
universal symbol categories.

Examples:

Python:
    function_definition

Java:
    method_declaration

JavaScript:
    function_declaration

React:
    arrow_function

ALL become:

    FUNCTION

React Components become:

    REACT_COMPONENT
"""

# =========================================================
# UNIVERSAL NODE GROUPS
# =========================================================
# basically it forms node groups where different languages from AST have functions but with different nomenclature
# so to group it in on we use AST NORMALIZER
# where we group all the similar ones under one name 
# sets are used beacuse unordered and fast search


NODE_GROUPS = {

    # =====================================================
    # FUNCTIONS
    # =====================================================

"FUNCTION": {

    # Python
    "function_definition",

    # Java
    "method_declaration",
    "constructor_declaration",

    # JavaScript
    "function_declaration",
    "function_expression",

    # Arrow functions
    "arrow_function",

    # TypeScript
    "method_signature",

    # Go
    "function_declaration",

    # Rust
    "function_item",

    # PHP
    "function_definition",
    "method_declaration",
    "anonymous_function_creation_expression",

    # C#
    "local_function_statement"
},

    # =====================================================
    # REACT COMPONENTS
    # =====================================================

    "REACT_COMPONENT": set(),

    # =====================================================
    # CLASSES
    # =====================================================

    "CLASS": {

        "class_definition",

        "class_declaration",

        "class",

        "class_body"
    },

    # =====================================================
    # INTERFACES
    # =====================================================

    "INTERFACE": {

        "interface_declaration",

        "interface_body"
    },

    # =====================================================
    # STRUCTS
    # =====================================================

    "STRUCT": {

        "struct_item",

        "struct_specifier",

        "struct_declaration"
    },

    # =====================================================
    # ENUMS
    # =====================================================

    "ENUM": {

        "enum_declaration",

        "enum_specifier"
    },

    # =====================================================
    # MODULES
    # =====================================================

    "MODULE": {

        "module",

        "module_declaration",

        "package_clause",

        "namespace_definition"
    },

    # =====================================================
    # IMPORTS
    # =====================================================

    "IMPORT": {

        # Python
        "import_statement",
        "import_from_statement",

        # JavaScript / TypeScript
        "import_statement",

        # C#
        "using_directive",
        "using_declaration",

        # Others
        "namespace_import"
    },

    # =====================================================
    # CALLS
    # =====================================================

    "CALL": {

    # Generic
    "call",
    "call_expression",

    # Java
    "method_invocation",

    # PHP
    "function_call",

    # Constructor calls
    "new_expression",

    # JS / TS
    "member_expression",

    # Python
    "attribute",

    # C / C++
    "field_expression"
},

    # =====================================================
    # VARIABLES
    # =====================================================

    "VARIABLE": {

        "assignment",

        "variable_declarator",

        "local_variable_declaration",

        "lexical_declaration"
    },

    # =====================================================
    # CONSTANTS
    # =====================================================

    "CONSTANT": {

        "const_item",

        "constant_declaration"
    },

    # =====================================================
    # COMMENTS
    # =====================================================

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
# HELPERS
# =========================================================


# checks the validity of the node
def is_function(node_type):

    return normalize_node_type(
        node_type
    ) == "FUNCTION"


def is_react_component(node_type):

    return normalize_node_type(
        node_type
    ) == "REACT_COMPONENT"


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

    "REACT_COMPONENT",

    "CLASS",

    "INTERFACE",

    "STRUCT",

    "ENUM",

    "MODULE",

    "IMPORT",

    "CALL",

    "VARIABLE",

    "CONSTANT"
]