# =========================================================
# SYMBOL REGISTRY
# =========================================================

def build_symbol_registry(symbols):

    registry = {}

    for symbol in symbols.get(
        "all_symbols",
        []
    ):

        qualified_name = symbol.get(
            "qualified_name"
        )

        if not qualified_name:
            continue

        registry[
            qualified_name
        ] = symbol

    return registry