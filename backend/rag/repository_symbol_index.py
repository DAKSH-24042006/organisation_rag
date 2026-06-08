# =========================================================
# REPOSITORY SYMBOL INDEX
# =========================================================

import os

from rag.parser import (
    get_repository_symbols
)

from rag.symbol_index import (
    build_symbol_index
)

# =========================================================
# COLLECT REPOSITORY SYMBOLS
# =========================================================

def collect_repository_symbols(

    repository_root

):

    all_symbols = []

    supported_extensions = {

        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx"
    }

    for root, _, files in os.walk(
        repository_root
    ):

        for file in files:

            extension = os.path.splitext(
                file
            )[1]

            if extension not in supported_extensions:

                continue

            file_path = os.path.join(
                root,
                file
            )

            try:

                with open(

                    file_path,

                    "r",

                    encoding="utf-8"

                ) as f:

                    source_code = f.read()

                symbols = get_repository_symbols(

                    source_code,

                    extension,

                    file_path=file_path
                )

                all_symbols.extend(

                    symbols.get(
                        "all_symbols",
                        []
                    )
                )

            except Exception as e:

                print(

                    "[SKIP]",

                    file_path,

                    str(e)
                )

    return all_symbols


# =========================================================
# BUILD REPOSITORY SYMBOL INDEX
# =========================================================

def build_repository_symbol_index(

    repository_root

):

    symbols = collect_repository_symbols(

        repository_root
    )

    return build_symbol_index(

        symbols
    )