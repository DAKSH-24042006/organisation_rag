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

    ".ts": Language(
        tree_sitter_typescript.language_typescript()
    ),

    ".java": Language(
        tree_sitter_java.language()
    )
}

# =========================================================
# NODE TYPES
# =========================================================

FUNCTION_NODES = {

    ".py": "function_definition",

    ".js": "function_declaration",

    ".ts": "function_declaration",

    ".java": "method_declaration"
}

CLASS_NODES = {

    ".py": "class_definition",

    ".js": "class_declaration",

    ".ts": "class_declaration",

    ".java": "class_declaration"
}

IMPORT_NODES = {

    ".py": [
        "import_statement",
        "import_from_statement"
    ],

    ".js": [
        "import_statement"
    ],

    ".ts": [
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

    language = LANGUAGES[extension]

    return Parser(language)

# =========================================================
# TREE TRAVERSAL
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

    parser = get_parser(extension)

    tree = parser.parse(
        bytes(code, "utf8")
    )

    return tree

# =========================================================
# EXTRACT FUNCTIONS
# =========================================================

def extract_functions(code, extension):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    functions = []

    target_node = FUNCTION_NODES[
        extension
    ]

    for node in traverse_tree(root):

        if node.type == target_node:

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

                "start_line":
                node.start_point[0] + 1,

                "end_line":
                node.end_point[0] + 1
            })

    return functions

# =========================================================
# EXTRACT CLASSES
# =========================================================

def extract_classes(code, extension):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    classes = []

    target_node = CLASS_NODES[
        extension
    ]

    for node in traverse_tree(root):

        if node.type == target_node:

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

                "start_line":
                node.start_point[0] + 1,

                "end_line":
                node.end_point[0] + 1
            })

    return classes

# =========================================================
# EXTRACT IMPORTS
# =========================================================

def extract_imports(code, extension):

    tree = parse_code(
        code,
        extension
    )

    root = tree.root_node

    imports = []

    target_nodes = IMPORT_NODES[
        extension
    ]

    for node in traverse_tree(root):

        if node.type in target_nodes:

            import_code = code[
                node.start_byte:
                node.end_byte
            ]

            imports.append(import_code)

    return list(set(imports))

# =========================================================
# EXTRACT DEPENDENCIES
# =========================================================

def extract_dependencies(code, extension):

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

                dependencies.append(dependency)

    return list(set(dependencies))