# =========================================================
# UNIVERSAL TREE-SITTER PARSER
# =========================================================

from tree_sitter_language_pack import get_parser

from rag.symbol_extractor import extract_symbols
from rag.call_graph import build_call_graph

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
    return EXTENSION_TO_LANGUAGE.get(extension)

# =========================================================
# GET PARSER
# =========================================================

def get_cached_parser(language):

    if language not in _PARSER_CACHE:
        _PARSER_CACHE[language] = get_parser(language)

    return _PARSER_CACHE[language]

# =========================================================
# PARSE CODE
# =========================================================

def parse_code(code, extension):

    language = get_language(extension)

    if language is None:
        return None

    parser = get_cached_parser(language)

    tree = parser.parse(code)

    return tree

# =========================================================
# EXTRACT SYMBOLS
# =========================================================

def get_repository_symbols(code, extension):

    tree = parse_code(
        code,
        extension
    )

    print(
    f"\n[DEBUG TREE] {extension}"
    )

    print(
        type(tree)
    )

    if tree is None:
        return {
            "functions": [],
            "classes": [],
            "interfaces": [],
            "structs": [],
            "enums": [],
            "modules": [],
            "imports": [],
            "calls": [],
            "all_symbols": []
        }

    return extract_symbols(
        tree,
        code
    )

# =========================================================
# CALL GRAPH
# =========================================================

def get_call_graph(code, extension):

    symbols = get_repository_symbols(
        code,
        extension
    )

    print("\n======================")
    print("FILE:", file_path)
    print("EXT:", extension)
    print("SYMBOLS KEYS:", symbols.keys())
    print("FUNCTIONS:", len(symbols.get("functions", [])))
    print("CLASSES:", len(symbols.get("classes", [])))
    print("IMPORTS:", len(symbols.get("imports", [])))
    print("CALLS:", len(symbols.get("calls", [])))
    print("======================\n")

    return build_call_graph(symbols)

# =========================================================
# FILE ANALYSIS
# =========================================================

def analyze_file(code, extension):

    symbols = get_repository_symbols(
        code,
        extension
    )

    graph = build_call_graph(symbols)

    return {
        "symbols": symbols,
        "call_graph": graph
    }

# =========================================================
# LEGACY FUNCTION API
# =========================================================

def extract_functions(code, extension):

    symbols = get_repository_symbols(
        code,
        extension
    )

    functions = []

    for symbol in symbols["functions"]:

        functions.append({
            "name": symbol["name"],
            "content": symbol["content"],
            "type": "function",
            "id": symbol["id"],
            "start_line": symbol["start_line"],
            "end_line": symbol["end_line"]
        })

    return functions

# =========================================================
# LEGACY CLASS API
# =========================================================

def extract_classes(code, extension):

    symbols = get_repository_symbols(
        code,
        extension
    )

    classes = []

    for symbol in symbols["classes"]:

        classes.append({
            "name": symbol["name"],
            "content": symbol["content"],
            "type": "class",
            "id": symbol["id"],
            "start_line": symbol["start_line"],
            "end_line": symbol["end_line"]
        })

    return classes

# =========================================================
# IMPORTS
# =========================================================

def extract_imports(code, extension):

    symbols = get_repository_symbols(
        code,
        extension
    )

    return symbols["imports"]

# =========================================================
# DEPENDENCIES
# =========================================================

def extract_dependencies(code, extension):

    symbols = get_repository_symbols(
        code,
        extension
    )

    return [
        call["name"]
        for call in symbols["calls"]
    ]

# =========================================================
# REACT COMPONENT DETECTION
# =========================================================

def extract_react_components(code, extension):

    components = []

    if extension not in [
        ".jsx",
        ".tsx",
        ".js",
        ".ts"
    ]:
        return components

    functions = extract_functions(
        code,
        extension
    )

    jsx_indicators = [
        "<div",
        "<span",
        "<button",
        "<form",
        "<input",
        "return ("
    ]

    for function in functions:

        content = function["content"]

        if any(
            token in content
            for token in jsx_indicators
        ):
            components.append({
                "name": function["name"],
                "content": content,
                "id": function["id"]
            })

    return components