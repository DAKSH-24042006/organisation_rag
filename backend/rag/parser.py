from tree_sitter import Language, Parser

import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_java

# =========================================================
# LANGUAGE CONFIG
# =========================================================

LANGUAGES = {

    ".py": Language(
        tree_sitter_python.language()
    ),

    ".js": Language(
        tree_sitter_javascript.language()
    ),

    ".jsx": Language(
        tree_sitter_javascript.language()
    ),

    ".ts": Language(
        tree_sitter_typescript.language_typescript()
    ),

    ".tsx": Language(
        tree_sitter_typescript.language_tsx()
    ),

    ".java": Language(
        tree_sitter_java.language()
    )
}

# =========================================================
# FUNCTION NODES
# =========================================================

FUNCTION_NODES = {

    ".py": [
        "function_definition"
    ],

    ".js": [
        "function_declaration",
        "method_definition"
    ],

    ".jsx": [
        "function_declaration",
        "method_definition"
    ],

    ".ts": [
        "function_declaration",
        "method_definition"
    ],

    ".tsx": [
        "function_declaration",
        "method_definition"
    ],

    ".java": [
        "method_declaration"
    ]
}

# =========================================================
# CLASS NODES
# =========================================================

CLASS_NODES = {

    ".py": [
        "class_definition"
    ],

    ".js": [
        "class_declaration"
    ],

    ".jsx": [
        "class_declaration"
    ],

    ".ts": [
        "class_declaration"
    ],

    ".tsx": [
        "class_declaration"
    ],

    ".java": [
        "class_declaration"
    ]
}

# =========================================================
# IMPORT NODES
# =========================================================

IMPORT_NODES = {

    ".py": [
        "import_statement",
        "import_from_statement"
    ],

    ".js": [
        "import_statement"
    ],

    ".jsx": [
        "import_statement"
    ],

    ".ts": [
        "import_statement"
    ],

    ".tsx": [
        "import_statement"
    ],

    ".java": [
        "import_declaration"
    ]
}

# =========================================================
# GET PARSER
# =========================================================

def get_parser(extension):

    parser = Parser(
        LANGUAGES[extension]
    )

    return parser

# =========================================================
# TREE WALKER
# =========================================================

def traverse_tree(node):

    stack = [node]

    while stack:

        current = stack.pop()

        yield current

        stack.extend(current.children)

# =========================================================
# PARSE CODE
# =========================================================

def parse_code(code, extension):

    parser = get_parser(
        extension
    )

    tree = parser.parse(
        bytes(code, "utf8")
    )

    return tree

# =========================================================
# EXTRACT REACT COMPONENTS
# =========================================================

def extract_react_components(

    code,
    extension
):

    if extension not in [
        ".jsx",
        ".tsx"
    ]:

        return []

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    components = []

    for node in traverse_tree(root):

        if node.type == "function_declaration":

            component_code = code[
                node.start_byte:
                node.end_byte
            ]

            if "return (" in component_code:

                component_name = "unknown"

                for child in node.children:

                    if child.type == "identifier":

                        component_name = code[
                            child.start_byte:
                            child.end_byte
                        ]

                components.append({

                    "name":
                    component_name,

                    "content":
                    component_code,

                    "type":
                    "react_component"
                })

    return components

# =========================================================
# EXTRACT FUNCTIONS
# =========================================================

def extract_functions(

    code,
    extension
):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    functions = []

    for node in traverse_tree(root):

        if node.type in FUNCTION_NODES[
            extension
        ]:

            function_code = code[
                node.start_byte:
                node.end_byte
            ]

            function_name = "unknown"

            for child in node.children:

                if child.type in [
                    "identifier",
                    "name"
                ]:

                    function_name = code[
                        child.start_byte:
                        child.end_byte
                    ]

            functions.append({

                "name":
                function_name,

                "content":
                function_code,

                "type":
                "function"
            })

    return functions

# =========================================================
# EXTRACT CLASSES
# =========================================================

def extract_classes(

    code,
    extension
):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    classes = []

    for node in traverse_tree(root):

        if node.type in CLASS_NODES[
            extension
        ]:

            class_code = code[
                node.start_byte:
                node.end_byte
            ]

            class_name = "unknown"

            for child in node.children:

                if child.type in [
                    "identifier",
                    "name"
                ]:

                    class_name = code[
                        child.start_byte:
                        child.end_byte
                    ]

            classes.append({

                "name":
                class_name,

                "content":
                class_code,

                "type":
                "class"
            })

    return classes

# =========================================================
# EXTRACT IMPORTS
# =========================================================

def extract_imports(

    code,
    extension
):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    imports = []

    for node in traverse_tree(root):

        if node.type in IMPORT_NODES[
            extension
        ]:

            import_code = code[
                node.start_byte:
                node.end_byte
            ]

            imports.append(import_code)

    return list(set(imports))

# =========================================================
# EXTRACT DEPENDENCIES
# =========================================================

def extract_dependencies(

    code,
    extension
):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    dependencies = []

    for node in traverse_tree(root):

        if node.type == "call":

            function_node = node.child_by_field_name(
                "function"
            )

            if function_node:

                dependency = code[
                    function_node.start_byte:
                    function_node.end_byte
                ]

                dependencies.append(
                    dependency
                )

    return list(set(dependencies))

import re

def extract_react_components(

    source_code,
    extension
):

    components = []

    if extension not in [

        ".js",
        ".jsx",
        ".ts",
        ".tsx"
    ]:

        return components

    # ============================================
    # FUNCTION COMPONENTS
    # ============================================

    function_pattern = re.finditer(

        r'const\s+([A-Z][A-Za-z0-9_]*)\s*=\s*\(.*?\)\s*=>\s*\{',

        source_code,

        re.DOTALL
    )

    for match in function_pattern:

        component_name = match.group(1)

        start = match.start()

        component_code = source_code[
            start:start + 4000
        ]

        components.append({

            "name": component_name,

            "content": component_code
        })

    # ============================================
    # FUNCTION DECLARATIONS
    # ============================================

    declaration_pattern = re.finditer(

        r'function\s+([A-Z][A-Za-z0-9_]*)\s*\(',

        source_code,

        re.DOTALL
    )

    for match in declaration_pattern:

        component_name = match.group(1)

        start = match.start()

        component_code = source_code[
            start:start + 4000
        ]

        components.append({

            "name": component_name,

            "content": component_code
        })

    return components