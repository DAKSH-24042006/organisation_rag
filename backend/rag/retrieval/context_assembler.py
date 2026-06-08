# =========================================================
# CONTEXT ASSEMBLER
# =========================================================

def assemble_context(

    retrieved_nodes,

    symbol_index

):

    context = []

    for node in retrieved_nodes:

        symbol = symbol_index.get(
            node
        )

        if not symbol:

            continue

        context.append(

            {

                "qualified_name":
                symbol.get(
                    "qualified_name"
                ),

                "type":
                symbol.get(
                    "symbol_type"
                ),

                "content":
                symbol.get(
                    "content"
                )
            }

        )

    return context