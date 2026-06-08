# returns the correct language extractor
from rag.symbol_extractors.extractor_router import (
    get_extractor
)

# =========================================================
# UNIVERSAL TREE-SITTER PARSER
# =========================================================

# gets the tree setter
from tree_sitter_language_pack import get_parser

# after syntax tree formed extracts useful entities
from rag.symbol_extractor import (
    extract_symbols
)

# helps in building relationships between functions
from rag.call_graph import (
    build_call_graph
)

# =========================================================
# LANGUAGE MAP
# =========================================================

# detects programming language through the file extension
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

# basically stores the language parser 
# so that u dont make again and again 
_PARSER_CACHE = {}

# =========================================================
# GET LANGUAGE
# =========================================================

# returns the language
def get_language(extension):

    return EXTENSION_TO_LANGUAGE.get(
        extension
    )

# =========================================================
# GET PARSER
# =========================================================

# if language not in cache the creates key for that lang and stores pareser object of that lang
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

    # get language
    language = get_language(
        extension
    )

    # if not found none so that no crash
    if language is None:

        return None

    # get the lang parser if exist reuse else make one 
    parser = get_cached_parser(
        language
    )

    # ensure string if not convert
    if not isinstance(
        code,
        str
    ):

        code = str(code)

    # debug log prints which lang
    print(
        f"[PARSER] {language}"
    )   

    # actual creation of the tree
    tree = parser.parse(
        code
    )

    return tree

# =========================================================
# SYMBOL EXTRACTION
# =========================================================

def get_repository_symbols(

    code,
    extension,
    file_path=None

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
        code,
        file_path=file_path
    )

# =========================================================
# CALL GRAPH
# =========================================================
# this is basically adding the symbols to the call graph
def get_call_graph(

    code,
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
        
    )

    return build_call_graph(
        symbols
    )

# =========================================================
# FILE ANALYSIS
# =========================================================
# actual formation of call graph and the symbols
def analyze_file(

    code,
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
    )

    graph = build_call_graph(
        symbols
    )

    return {

        "symbols": symbols,

        "call_graph": graph
    }




# next ones are helper functions technically we can do it without these
# =========================================================
# HELPERS
# =========================================================

def extract_functions(

    code,
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
    )

    return symbols[
        "functions"
    ]

# =========================================================
# REACT COMPONENTS
# =========================================================

def extract_react_components(

    code,
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
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
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
    )

    return symbols[
        "classes"
    ]

# =========================================================
# IMPORTS
# =========================================================

def extract_imports(

    code,
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
    )

    return symbols[
        "imports"
    ]

# =========================================================
# DEPENDENCIES
# =========================================================

def extract_dependencies(

    code,
    extension,
    file_path=None

):

    symbols = get_repository_symbols(

        code,
        extension,
        file_path=file_path
    )

    return [

        call["name"]

        for call in symbols.get(
            "calls",
            []
        )
    ]