# =========================================================
# V2 SYMBOL EXTRACTOR MODULE
# =========================================================

import os
import re

# Node extraction helpers
def get_node_type(node) -> str:
    """Safely get node type or kind from Tree-sitter node."""
    t = getattr(node, "type", None)
    if t is not None:
        t_val = t() if callable(t) else t
        if isinstance(t_val, str):
            return t_val
    k = getattr(node, "kind", None)
    if k is not None:
        k_val = k() if callable(k) else k
        if isinstance(k_val, str):
            return k_val
    return ""

def get_node_line(node, boundary="start") -> int:
    """Safely get 0-indexed line number for start or end of node."""
    p = getattr(node, f"{boundary}_position", None)
    if p is not None:
        pos = p() if callable(p) else p
        if hasattr(pos, "row"):
            return pos.row
        elif isinstance(pos, (tuple, list)) and len(pos) > 0:
            return pos[0]

    pt = getattr(node, f"{boundary}_point", None)
    if pt is not None:
        point = pt() if callable(pt) else pt
        if hasattr(point, "row"):
            return point.row
        elif isinstance(point, (tuple, list)) and len(point) > 0:
            return point[0]
    return 0

def get_node_byte(node, boundary="start") -> int:
    """Safely get start or end byte offset."""
    b = getattr(node, f"{boundary}_byte", None)
    if b is not None:
        return b() if callable(b) else b
    return 0

def extract_node_name(node, source_bytes: bytes) -> str:
    """Recursively search for an identifier or name node under the given node."""
    TARGET_TYPES = {
        "identifier",
        "name",
        "property_identifier",
        "type_identifier",
        "field_identifier",
        "shorthand_property_identifier",
        "variable_name"
    }
    
    node_type = get_node_type(node)
    if node_type in TARGET_TYPES:
        start_byte = get_node_byte(node, "start")
        end_byte = get_node_byte(node, "end")
        val_bytes = source_bytes[start_byte:end_byte]
        val = val_bytes.decode("utf-8", errors="ignore").strip()
        if val:
            return val
            
    # Iterate through children
    child_count = getattr(node, "child_count", 0)
    if callable(child_count):
        child_count = child_count()
        
    for i in range(child_count):
        child = node.child(i)
        if child:
            name = extract_node_name(child, source_bytes)
            if name:
                return name
    return ""

# Universal Node mapping logic
NODE_GROUPS = {
    "CLASS": {
        "class_definition",
        "class_declaration",
        "class",
        "class_body"
    },
    "FUNCTION": {
        "function_definition",
        "method_declaration",
        "constructor_declaration",
        "function_declaration",
        "function_expression",
        "arrow_function",
        "method_signature",
        "function_item",
        "anonymous_function_creation_expression",
        "local_function_statement"
    },
    "IMPORT": {
        "import_statement",
        "import_from_statement",
        "using_directive",
        "using_declaration",
        "namespace_import"
    },
    "CALL": {
        "call",
        "call_expression",
        "method_invocation",
        "function_call",
        "new_expression",
        "member_expression",
        "attribute",
        "field_expression"
    }
}

REVERSE_MAP = {}
for cat, types in NODE_GROUPS.items():
    for t in types:
        REVERSE_MAP[t] = cat

def normalize_node_type(node_type: str) -> str:
    return REVERSE_MAP.get(node_type, "OTHER")

class SymbolExtractor:
    """Walks the AST using Tree-sitter and extracts symbols with stable node IDs."""
    
    @staticmethod
    def extract_symbols(parse_result: dict, relative_path: str) -> list:
        """Extracts code symbols from a parse result."""
        file_type = parse_result.get("type")
        if file_type != "CODE":
            # Config / Docs symbols are already extracted by parser.py
            symbols = parse_result.get("symbols", [])
            # Enrich with stable node IDs
            for s in symbols:
                s["id"] = f"{relative_path}::{s['qualified_name']}"
                s["repository_path"] = relative_path
            return symbols
            
        tree = parse_result.get("tree")
        source_code = parse_result.get("raw_content", "")
        language = parse_result.get("language", "")
        
        if not tree:
            return []
            
        root = tree.root_node() if callable(tree.root_node) else tree.root_node
        source_bytes = source_code.encode("utf-8")
        extracted = []
        
        # Traverse with a stack of (node, parent_qualified_name)
        # to correctly build qualified names (e.g. Class.method)
        stack = [(root, "")]
        
        while stack:
            node, parent_qual = stack.pop()
            node_type = get_node_type(node)
            norm_type = normalize_node_type(node_type)
            
            # Skip AST container helper nodes
            if node_type == "class":
                # For some languages, 'class' is just a keyword node
                # Skip children exploration of it directly
                continue
                
            current_qual = parent_qual
            
            if norm_type in {"CLASS", "FUNCTION", "IMPORT", "CALL"}:
                name = extract_node_name(node, source_bytes)
                
                # Filter fake symbols or anonymous symbols
                # Never generate class_0, function_1
                if not name or name.strip() == "":
                    # Skip anonymous functions and arrow callback lambdas
                    # but traverse children
                    pass
                else:
                    start_line = get_node_line(node, "start") + 1
                    end_line = get_node_line(node, "end") + 1
                    
                    start_byte = get_node_byte(node, "start")
                    end_byte = get_node_byte(node, "end")
                    content = source_bytes[start_byte:end_byte].decode("utf-8", errors="ignore")
                    
                    # Compute qualified name
                    if norm_type == "CLASS":
                        current_qual = f"{parent_qual}.{name}" if parent_qual else name
                        qname = current_qual
                    elif norm_type == "FUNCTION":
                        qname = f"{parent_qual}.{name}" if parent_qual else name
                    else:
                        qname = name
                        
                    # Stable Node ID
                    node_id = f"{relative_path}::{qname}"
                    
                    symbol = {
                        "id": node_id,
                        "name": name,
                        "qualified_name": qname,
                        "symbol_type": norm_type,
                        "start_line": start_line,
                        "end_line": end_line,
                        "content": content,
                        "repository_path": relative_path,
                        "language": language
                    }
                    
                    # Language-specific enrichment
                    if language == "python":
                        SymbolExtractor._enrich_python(symbol, source_bytes, node)
                    elif language in {"javascript", "typescript", "tsx"}:
                        SymbolExtractor._enrich_js(symbol, source_code, node)
                        
                    extracted.append(symbol)
            
            # Push children to stack in reverse order for DFS
            child_count = getattr(node, "child_count", 0)
            if callable(child_count):
                child_count = child_count()
            
            for i in range(child_count - 1, -1, -1):
                child = node.child(i)
                if child:
                    stack.append((child, current_qual))
                    
        return extracted

    @staticmethod
    def _enrich_python(symbol: dict, source_bytes: bytes, node):
        """Extract python annotations, async status, decorators, routes."""
        content = symbol.get("content", "")
        symbol["is_async"] = content.startswith("async def ")
        
        # Extract decorators
        decorators = []
        
        # Safe traversal of parent node
        parent_func = getattr(node, "parent", None)
        parent = parent_func() if callable(parent_func) else parent_func
        parent_kind = parent.kind() if parent else None
        
        if parent_kind == "decorated_definition":
            for i in range(parent.child_count()):
                child = parent.child(i)
                if child.kind() == "decorator":
                    dec_text = source_bytes[child.start_byte():child.end_byte()].decode("utf-8", errors="ignore")
                    decorators.append(dec_text)
                    
        symbol["decorators"] = decorators
        
        # Check FastAPI routes
        if symbol["symbol_type"] == "FUNCTION" and decorators:
            # Match app.get(..., tags=...) or router.post(...)
            route_pattern = re.compile(r'@(router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', re.DOTALL)
            for dec in decorators:
                m = route_pattern.search(dec)
                if m:
                    symbol["framework"] = "FastAPI"
                    symbol["component_type"] = "API_ROUTE"
                    symbol["http_method"] = m.group(2).upper()
                    symbol["route"] = m.group(3)
                    break
                    
        # Check Pydantic models
        if symbol["symbol_type"] == "CLASS" and "BaseModel" in content:
            symbol["framework"] = "Pydantic"
            symbol["component_type"] = "MODEL"

    @staticmethod
    def _enrich_js(symbol: dict, source_code: str, node):
        """Extract React, NextJS, or Redux properties."""
        content = symbol.get("content", "")
        name = symbol.get("name", "")
        
        # React component check
        is_component = False
        if name and name[0].isupper() and symbol["symbol_type"] in {"FUNCTION", "CLASS"}:
            is_component = True
        if "return (" in content or "<div" in content:
            is_component = True
            
        if is_component:
            symbol["framework"] = "React"
            symbol["component_type"] = "COMPONENT"
            
        # React Hooks used
        hooks_list = ["useState", "useEffect", "useMemo", "useCallback", "useRef", "useContext"]
        found_hooks = [h for h in hooks_list if h in content]
        if found_hooks:
            symbol["hooks"] = found_hooks
            
        # NextJS API routes
        if "NextResponse" in content:
            symbol["framework"] = "NextJS"
            symbol["component_type"] = "API_ROUTE"
            
        # Redux Slice
        if "createSlice(" in content:
            symbol["framework"] = "Redux"
            symbol["component_type"] = "SLICE"