# =========================================================
# UNIVERSAL SYMBOL EXTRACTOR
# =========================================================

import hashlib

from rag.ast_normalizer import (
    normalize_node_type,
    SUPPORTED_SYMBOL_TYPES
)

# =========================================================
# TREE-SITTER NODE PROPERTIES COMPATIBILITY
# =========================================================

def get_node_type(node):
    # Try 'type'
    t = getattr(node, "type", None)
    if t is not None:
        if callable(t):
            t_val = t()
        else:
            t_val = t
        if isinstance(t_val, str):
            return t_val

    # Try 'kind'
    k = getattr(node, "kind", None)
    if k is not None:
        if callable(k):
            k_val = k()
        else:
            k_val = k
        if isinstance(k_val, str):
            return k_val
    return ""

def get_node_byte(node, name="start"):
    b = getattr(node, f"{name}_byte", None)
    if b is not None:
        if callable(b):
            return b()
        return b
    return 0

def get_node_line(node, name="start"):
    # Try 'start_position' / 'end_position'
    p = getattr(node, f"{name}_position", None)
    if p is not None:
        pos = p() if callable(p) else p
        if hasattr(pos, "row"):
            return pos.row
        elif isinstance(pos, (tuple, list)) and len(pos) > 0:
            return pos[0]

    # Try 'start_point' / 'end_point'
    pt = getattr(node, f"{name}_point", None)
    if pt is not None:
        point = pt() if callable(pt) else pt
        if hasattr(point, "row"):
            return point.row
        elif isinstance(point, (tuple, list)) and len(point) > 0:
            return point[0]
    return 0

# =========================================================
# CHILD COUNT COMPATIBILITY
# =========================================================

def get_child_count(node):

    count = node.child_count

    if callable(count):
        return count()

    return count

# =========================================================
# EXTRACT NODE NAME
# =========================================================

def extract_node_name(
    node,
    source_code
):

    TARGET_TYPES = {

        "identifier",
        "name",
        "property_identifier",
        "type_identifier",
        "field_identifier",
        "shorthand_property_identifier",
        "variable_name"
    }

    try:

        stack = [node]

        while stack:

            current = stack.pop()

            node_type = get_node_type(
                current
            )

            if node_type in TARGET_TYPES:

                start_byte = get_node_byte(
                    current,
                    "start"
                )

                end_byte = get_node_byte(
                    current,
                    "end"
                )

                name = source_code[
                    start_byte:end_byte
                ]

                if (
                    name
                    and len(name.strip()) > 0
                ):
                    return name.strip()

            child_count = get_child_count(
                current
            )

            for i in reversed(
                range(child_count)
            ):

                child = current.child(i)

                if child is not None:

                    stack.append(
                        child
                    )

    except Exception:

        pass

    return None

# =========================================================
# SYMBOL ID
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
# CREATE SYMBOL
# =========================================================

def create_symbol(

    node,
    source_code,
    symbol_type,
    parent_id=None

):

    start_byte = get_node_byte(node, "start")
    end_byte = get_node_byte(node, "end")
    content = source_code[
        start_byte:
        end_byte
    ]

    name = extract_node_name(
        node,
        source_code
    )

    start_row = get_node_line(node, "start")
    end_row = get_node_line(node, "end")

    if not name:

        name = (
            f"{symbol_type.lower()}_"
            f"{start_row}"
        )

    start_line = start_row + 1
    end_line = end_row + 1

    symbol_id = generate_symbol_id(

        symbol_type,
        name,
        start_line
    )

    return {

        "id": symbol_id,

        "name": name,

        "symbol_type": symbol_type,

        "start_line": start_line,

        "end_line": end_line,

        "parent": parent_id,

        "children": [],

        "content": content
    }

# =========================================================
# EXTRACT SYMBOLS
# =========================================================

def extract_symbols(

    tree,
    source_code

):

    if callable(tree.root_node):

        root = tree.root_node()

    else:

        root = tree.root_node

    symbols = {

        "functions": [],
        "react_components": [],
        "classes": [],
        "interfaces": [],
        "structs": [],
        "enums": [],
        "modules": [],
        "imports": [],
        "calls": [],
        "variables": [],
        "constants": [],
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

        node_type = get_node_type(
            node
        )

        symbol_type = normalize_node_type(
            node_type
        )

        # =========================================
        # REACT COMPONENT DETECTION
        # =========================================

        if node_type == "arrow_function":

            component_name = extract_node_name(
                node,
                source_code
            )

            if (
                component_name
                and len(component_name) > 0
                and component_name[0].isupper()
            ):

                symbol_type = "REACT_COMPONENT"

            else:

                symbol_type = "FUNCTION"

        current_symbol_id = parent_id

        if symbol_type in SUPPORTED_SYMBOL_TYPES:

            symbol = create_symbol(

                node=node,
                source_code=source_code,
                symbol_type=symbol_type,
                parent_id=parent_id
            )

            print(
                f"[DEBUG] Symbol extracted: "
                f"name={symbol['name']}, "
                f"type={symbol_type}, "
                f"lines={symbol['start_line']}-{symbol['end_line']}"
            )

            current_symbol_id = symbol[
                "id"
            ]

            symbols[
                "all_symbols"
            ].append(symbol)

            if symbol_type == "FUNCTION":

                symbols[
                    "functions"
                ].append(symbol)

            elif symbol_type == "REACT_COMPONENT":

                symbols[
                    "react_components"
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

            elif symbol_type == "VARIABLE":

                symbols[
                    "variables"
                ].append(symbol)

            elif symbol_type == "CONSTANT":

                symbols[
                    "constants"
                ].append(symbol)

        # =========================================
        # DFS WALK
        # =========================================

        for i in reversed(

            range(
                get_child_count(
                    node
                )
            )
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
# BUILD SYMBOL MAP
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
# BUILD FUNCTION MAP
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