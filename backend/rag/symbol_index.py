# =========================================================
# SYMBOL INDEX
# =========================================================

"""
Repository-wide symbol lookup.

Used for:

CALL -> FUNCTION resolution
Cross-file symbol lookup
Dependency analysis
Graph expansion
"""


# =========================================================
# BUILD SYMBOL INDEX
# =========================================================

def build_symbol_index(

    all_symbols

):

    index = {}

    valid_symbol_types = {

        "FUNCTION",

        "CLASS",

        "INTERFACE",

        "STRUCT",

        "ENUM"

    }

    for symbol in all_symbols:

        symbol_type = symbol.get(
            "symbol_type"
        )

        if symbol_type not in valid_symbol_types:

            continue

        # =====================================
        # QUALIFIED NAME LOOKUP
        # =====================================

        qualified_name = symbol.get(
            "qualified_name"
        )

        if qualified_name:

            index[
                qualified_name
            ] = symbol

        # =====================================
        # SHORT NAME LOOKUP
        # =====================================

        name = symbol.get(
            "name"
        )

        if name:

            if name not in index:

                index[
                    name
                ] = symbol

    return index


# =========================================================
# RESOLVE SYMBOL
# =========================================================

def resolve_symbol(

    symbol_name,

    symbol_index

):

    return symbol_index.get(
        symbol_name
    )