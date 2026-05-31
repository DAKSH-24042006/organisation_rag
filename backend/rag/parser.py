from rag.symbol_extractors.extractor_router import (
    get_extractor
)

# =========================================================
# UNIVERSAL TREE-SITTER PARSER
# =========================================================

from tree_sitter_language_pack import get_parser

from rag.symbol_extractor import (
    extract_symbols
)

from rag.call_graph import (
    build_call_graph
)

# =========================================================
# LANGUAGE MAP
# =========================================================

EXTENSION_TO_LANGUAGE = {

    ".py": "python",

    ".js": "javascript",

    ".jsx": "javascript",

    ".ts": "typescript",

    ".tsx": "tsx",

    ".java": "java",

    ".php": "php",

    ".go": "go",

    ".rs": "rust",

    ".c": "c",

    ".cpp": "cpp",

    ".cc": "cpp",

    ".cxx": "cpp",

    ".cs": "c_sharp",

    ".rb": "ruby",

    ".kt": "kotlin",

    ".swift": "swift",

    ".scala": "scala",

    ".lua": "lua",

    ".sh": "bash"
}

# =========================================================
# PARSER CACHE
# =========================================================

_PARSER_CACHE = {}

# =========================================================
# GET LANGUAGE
# =========================================================

def get_language(extension):

    return EXTENSION_TO_LANGUAGE.get(
        extension
    )

# =========================================================
# GET PARSER
# =========================================================

def get_cached_parser(language):

    if language not in _PARSER_CACHE:

        _PARSER_CACHE[
            language
        ] = get_parser(
            language
        )

    return _PARSER_CACHE[
        language
    ]

# =========================================================
# PARSE CODE
# =========================================================

def parse_code(

    code,
    extension

):

    language = get_language(
        extension
    )

    if language is None:

        return None

    parser = get_cached_parser(
        language
    )

    # ensure string
    if not isinstance(
        code,
        str
    ):

        code = str(code)

    print(
        f"[PARSER] {language}"
    )   

    tree = parser.parse(
        code
    )

    return tree

# =========================================================
# SYMBOL EXTRACTION
# =========================================================

def get_repository_symbols(

    code,
    extension

):

    tree = parse_code(

        code,
        extension
    )

    if tree is None:

        return {

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

    language = get_language(
        extension
    )

    extractor = get_extractor(
        language
    )

    return extractor.extract(

        tree,
        code
    )

# =========================================================
# CALL GRAPH
# =========================================================

def get_call_graph(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    return build_call_graph(
        symbols
    )

# =========================================================
# FILE ANALYSIS
# =========================================================

def analyze_file(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    graph = build_call_graph(
        symbols
    )

    return {

        "symbols": symbols,

        "call_graph": graph
    }



# =========================================================
# HELPERS
# =========================================================

def extract_functions(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    return symbols[
        "functions"
    ]

# =========================================================
# REACT COMPONENTS
# =========================================================

def extract_react_components(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    return symbols.get(

        "react_components",

        []
    )

# =========================================================
# CLASSES
# =========================================================

def extract_classes(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    return symbols[
        "classes"
    ]

# =========================================================
# IMPORTS
# =========================================================

def extract_imports(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    return symbols[
        "imports"
    ]

# =========================================================
# DEPENDENCIES
# =========================================================

def extract_dependencies(

    code,
    extension

):

    symbols = get_repository_symbols(

        code,
        extension
    )

    return [

        call["name"]

        for call in symbols.get(
            "calls",
            []
        )
    ]