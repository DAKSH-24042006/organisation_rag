from rag.symbol_extractors.base_extractor import (
    BaseExtractor
)

from rag.symbol_extractors.js_extractor import (
    JavaScriptExtractor
)

from rag.symbol_extractors.python_extractor import (
    PythonExtractor
)

from rag.symbol_extractors.java_extractor import (
    JavaExtractor
)

from rag.symbol_extractors.cpp_extractor import (
    CppExtractor
)

from rag.symbol_extractors.php_extractor import (
    PhpExtractor
)


EXTRACTOR_MAP = {

    "javascript": JavaScriptExtractor(),

    "typescript": JavaScriptExtractor(),

    "tsx": JavaScriptExtractor(),

    "python": PythonExtractor(),

    "java": JavaExtractor(),

    "cpp": CppExtractor(),

    "c": CppExtractor(),

    "php": PhpExtractor()
}


def get_extractor(
    language
):

    return EXTRACTOR_MAP.get(
        language,
        BaseExtractor()
    )