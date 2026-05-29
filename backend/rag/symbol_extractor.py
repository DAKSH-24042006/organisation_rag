# =========================================================
# UNIVERSAL SYMBOL EXTRACTOR
# =========================================================

def get_child_count(node):

    count = node.child_count

    if callable(count):
        return count()

    return count

import hashlib

from rag.ast_normalizer import (

    normalize_node_type,

    SUPPORTED_SYMBOL_TYPES
)

# =========================================================
# EXTRACT NODE NAME
# =========================================================

def extract_node_name(

    node,
    source_code

):

    try:

        for child in node.children:

            if child.type in [

                "identifier",

                "name",

                "property_identifier",

                "type_identifier"
            ]:

                return source_code[
                    child.start_byte:
                    child.end_byte
                ]

    except Exception:

        pass

    return None

# =========================================================
# GENERATE SYMBOL ID
# =========================================================

def generate_symbol_id(

    symbol_type,
    name,
    start_line

):

    value = (

        f"{symbol_type}:"
        f"{name}:"
        f"{start_line}"
    )

    return hashlib.md5(

        value.encode()

    ).hexdigest()

# =========================================================
# CREATE SYMBOL OBJECT
# =========================================================

def create_symbol(

    node,
    source_code,
    symbol_type,
    parent_id=None

):

    content = source_code[
        node.start_byte:
        node.end_byte
    ]

    name = extract_node_name(

        node,
        source_code
    )

    if not name:

        name = f"{symbol_type.lower()}_" \
               f"{node.start_point[0]}"

    start_line = (

        node.start_point[0] + 1
    )

    end_line = (

        node.end_point[0] + 1
    )

    symbol_id = generate_symbol_id(

        symbol_type,

        name,

        start_line
    )

    return {

        "id":
        symbol_id,

        "name":
        name,

        "symbol_type":
        symbol_type,

        "start_line":
        start_line,

        "end_line":
        end_line,

        "parent":
        parent_id,

        "children":
        [],

        "content":
        content
    }

# =========================================================
# EXTRACT SYMBOLS
# =========================================================

def extract_symbols(

    tree,
    source_code

):

# =========================================================
# TREE-SITTER VERSION COMPATIBILITY
# =========================================================

    if callable(tree.root_node):

        root = tree.root_node()

    else:

        root = tree.root_node

    print(
        "[DEBUG ROOT]",
        type(root)
    )

    symbols = {

        "functions": [],
        "classes": [],
        "interfaces": [],
        "structs": [],
        "enums": [],
        "modules": [],
        "imports": [],
        "calls": [],

        # future graph support
        "all_symbols": []
    }

    stack = [

        (
            root,
            None
        )
    ]

    while stack:

        node, parent_id = stack.pop()

        symbol_type = normalize_node_type(
           node.kind
        )

        current_symbol_id = parent_id

        if (

            symbol_type
            in
            SUPPORTED_SYMBOL_TYPES

        ):

            symbol = create_symbol(

                node,
                source_code,
                symbol_type,
                parent_id
            )

            current_symbol_id = symbol[
                "id"
            ]

            symbols[
                "all_symbols"
            ].append(
                symbol
            )

            if symbol_type == "FUNCTION":

                symbols[
                    "functions"
                ].append(symbol)

            elif symbol_type == "CLASS":

                symbols[
                    "classes"
                ].append(symbol)

            elif symbol_type == "INTERFACE":

                symbols[
                    "interfaces"
                ].append(symbol)

            elif symbol_type == "STRUCT":

                symbols[
                    "structs"
                ].append(symbol)

            elif symbol_type == "ENUM":

                symbols[
                    "enums"
                ].append(symbol)

            elif symbol_type == "MODULE":

                symbols[
                    "modules"
                ].append(symbol)

            elif symbol_type == "IMPORT":

                symbols[
                    "imports"
                ].append(symbol)

            elif symbol_type == "CALL":

                symbols[
                    "calls"
                ].append(symbol)

        child_count = node.child_count

        if callable(child_count):
            child_count = child_count()

        for i in reversed(
            range(get_child_count(node))
        ):

            child = node.child(i)

            if child is not None:

                stack.append(
                    (
                        child,
                        current_symbol_id
                    )
                )

    return symbols

# =========================================================
# LOOKUP HELPERS
# =========================================================

def get_symbol_by_id(

    symbols,
    symbol_id

):

    for symbol in symbols[
        "all_symbols"
    ]:

        if symbol["id"] == symbol_id:

            return symbol

    return None

# =========================================================
# GET SYMBOL MAP
# =========================================================

def build_symbol_map(

    symbols

):

    return {

        symbol["id"]: symbol

        for symbol in symbols[
            "all_symbols"
        ]
    }

# =========================================================
# GET FUNCTION MAP
# =========================================================

def build_function_map(

    symbols

):

    return {

        symbol["name"]: symbol

        for symbol in symbols[
            "functions"
        ]
    }