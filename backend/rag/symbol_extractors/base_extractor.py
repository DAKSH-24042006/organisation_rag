# =========================================================
# BASE EXTRACTOR
# =========================================================

from rag.symbol_extractor import extract_symbols


class BaseExtractor:

    def extract(
        self,
        tree,
        source_code,
        file_path=None
    ):
        return extract_symbols(
            tree,
            source_code,
            file_path=file_path
        )