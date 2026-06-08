# =========================================================
# IMPORT RESOLVER
# =========================================================

import os

# =========================================================
# RESOLVE PYTHON IMPORT
# =========================================================

def resolve_python_import(

    import_module,
    repository_root

):

    if not import_module:

        return None

    relative_path = (

        import_module
        .replace(
            ".",
            "/"
        )

        + ".py"
    )

    for root, _, files in os.walk(
        repository_root
    ):

        for file in files:

            full_path = os.path.join(
                root,
                file
            )

            normalized = full_path.replace(
                "\\",
                "/"
            )

            if normalized.endswith(
                relative_path
            ):

                return normalized

    return None
