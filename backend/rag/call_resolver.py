# =========================================================
# CALL RESOLVER
# =========================================================

from rag.symbol_index import (
    resolve_symbol
)

# =========================================================
# RESOLVE CALL
# =========================================================

def resolve_call(

    call_symbol,

    symbol_index

):

    call_name = call_symbol.get(
        "name"
    )

    if not call_name:

        return None

    return resolve_symbol(

        call_name,

        symbol_index
    )