# =========================================================
# V2 UNIFIED PARSER MODULE
# =========================================================

import os
import json
import yaml
import re

# Resilient Tree-Sitter imports
try:
    from tree_sitter_language_pack import get_parser as ts_get_parser
except ImportError:
    try:
        from tree_sitter_languages import get_parser as ts_get_parser
    except ImportError:
        print("[WARNING] Could not import tree-sitter parser helper. Code parsing will be unavailable.")
        ts_get_parser = None

# Extension Mappings
TREESITTER_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "cpp",
    ".h": "cpp",
    ".php": "php",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby"
}

CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".env"}
MARKUP_EXTENSIONS = {".md", ".rst", ".html"}
FLATFILE_EXTENSIONS = {".sql", ".sh", "Dockerfile", "Makefile", ".gitignore"}

_PARSER_CACHE = {}

def get_cached_parser(language: str):
    """Reuse parser instances to save overhead."""
    if not ts_get_parser:
        return None
    if language not in _PARSER_CACHE:
        try:
            _PARSER_CACHE[language] = ts_get_parser(language)
        except Exception as e:
            print(f"[WARNING] Failed to load tree-sitter parser for {language}: {e}")
            _PARSER_CACHE[language] = None
    return _PARSER_CACHE[language]

class FileParser:
    """Orchestrates parsing of files based on their type."""
    
    @staticmethod
    def parse_file(file_path: str, source_code: str) -> dict:
        """Parses a file and returns extracted raw symbols/contents."""
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # 1. TreeSitter Parser
        if ext in TREESITTER_EXTENSIONS:
            return FileParser._parse_treesitter(file_path, source_code, TREESITTER_EXTENSIONS[ext])
            
        # 2. Config Parser
        if ext in CONFIG_EXTENSIONS:
            return FileParser._parse_config(file_path, source_code, ext)
            
        # 3. Markup Parser
        if ext in MARKUP_EXTENSIONS:
            return FileParser._parse_markup(file_path, source_code, ext)
            
        # 4. Flatfile Parser
        if ext in FLATFILE_EXTENSIONS or filename in FLATFILE_EXTENSIONS:
            return FileParser._parse_flatfile(file_path, source_code, filename, ext)
            
        # Fallback empty structure
        return FileParser._empty_result()
        
    @staticmethod
    def _empty_result() -> dict:
        return {
            "type": "UNKNOWN",
            "symbols": [],
            "imports": [],
            "calls": [],
            "raw_content": ""
        }

    @staticmethod
    def _parse_treesitter(file_path: str, source_code: str, language: str) -> dict:
        """Parses source code into AST trees."""
        parser = get_cached_parser(language)
        if not parser:
            return FileParser._empty_result()
            
        try:
            tree = parser.parse(source_code)
            return {
                "type": "CODE",
                "language": language,
                "tree": tree,
                "raw_content": source_code
            }
        except Exception as e:
            print(f"[ERROR] Tree-sitter parsing failed for {file_path}: {e}")
            return FileParser._empty_result()

    @staticmethod
    def _parse_config(file_path: str, source_code: str, ext: str) -> dict:
        """Parses JSON, YAML, or .env files."""
        symbols = []
        try:
            if ext == ".json":
                data = json.loads(source_code)
                symbols = FileParser._flatten_config(data)
            elif ext in {".yaml", ".yml"}:
                data = yaml.safe_load(source_code)
                if data:
                    symbols = FileParser._flatten_config(data)
            elif ext == ".env":
                for idx, line in enumerate(source_code.splitlines(), 1):
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    symbols.append({
                        "name": key.strip(),
                        "qualified_name": key.strip(),
                        "symbol_type": "ENV_VAR",
                        "content": val.strip(),
                        "start_line": idx,
                        "end_line": idx
                    })
            
            return {
                "type": "CONFIG",
                "symbols": symbols,
                "raw_content": source_code
            }
        except Exception as e:
            print(f"[ERROR] Config parsing failed for {file_path}: {e}")
            return FileParser._empty_result()

    @staticmethod
    def _flatten_config(data, prefix="") -> list:
        results = []
        if not isinstance(data, dict):
            return results
        for k, v in data.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                results.extend(FileParser._flatten_config(v, full_key))
            else:
                results.append({
                    "name": k,
                    "qualified_name": full_key,
                    "symbol_type": "CONFIG_KEY",
                    "content": str(v),
                    "start_line": 0,
                    "end_line": 0
                })
        return results

    @staticmethod
    def _parse_markup(file_path: str, source_code: str, ext: str) -> dict:
        """Parses Markdown, RST, or HTML files into section-based symbols."""
        symbols = []
        try:
            if ext == ".md":
                # Extract headers and sections
                current_hdr = "Overview"
                current_body = []
                start_line = 1
                for idx, line in enumerate(source_code.splitlines(), 1):
                    if line.startswith("#"):
                        if current_body:
                            symbols.append({
                                "name": current_hdr,
                                "qualified_name": current_hdr,
                                "symbol_type": "DOC_SECTION",
                                "content": "\n".join(current_body),
                                "start_line": start_line,
                                "end_line": idx - 1
                            })
                        current_hdr = line.lstrip("#").strip()
                        current_body = []
                        start_line = idx
                    else:
                        current_body.append(line)
                if current_body:
                    symbols.append({
                        "name": current_hdr,
                        "qualified_name": current_hdr,
                        "symbol_type": "DOC_SECTION",
                        "content": "\n".join(current_body),
                        "start_line": start_line,
                        "end_line": len(source_code.splitlines())
                    })
            elif ext == ".rst":
                lines = source_code.splitlines()
                for idx in range(len(lines) - 1):
                    title = lines[idx].strip()
                    underline = lines[idx+1].strip()
                    if underline and set(underline) in [{"="}, {"-"}, {"~"}]:
                        symbols.append({
                            "name": title,
                            "qualified_name": title,
                            "symbol_type": "DOC_SECTION",
                            "content": title,
                            "start_line": idx + 1,
                            "end_line": idx + 2
                        })
            elif ext == ".html":
                headings = re.finditer(r"<h([1-6])>(.*?)</h\1>", source_code, re.IGNORECASE)
                for match in headings:
                    symbols.append({
                        "name": match.group(2).strip(),
                        "qualified_name": match.group(2).strip(),
                        "symbol_type": "DOC_SECTION",
                        "content": match.group(0),
                        "start_line": 0,
                        "end_line": 0
                    })
            
            return {
                "type": "DOCUMENTATION",
                "symbols": symbols,
                "raw_content": source_code
            }
        except Exception as e:
            print(f"[ERROR] Markup parsing failed for {file_path}: {e}")
            return FileParser._empty_result()

    @staticmethod
    def _parse_flatfile(file_path: str, source_code: str, filename: str, ext: str) -> dict:
        """Parses flat file definitions like SQL, Dockerfile, Makefile, etc."""
        symbols = []
        try:
            if ext == ".sql":
                # Extract CREATE TABLE statements
                matches = re.finditer(r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);", source_code, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    table_name = match.group(1)
                    body = match.group(0)
                    # Simple line calculation
                    start = source_code[:match.start()].count("\n") + 1
                    end = start + body.count("\n")
                    symbols.append({
                        "name": table_name,
                        "qualified_name": table_name,
                        "symbol_type": "SQL_TABLE",
                        "content": body.strip(),
                        "start_line": start,
                        "end_line": end
                    })
            elif ext == ".sh":
                # Simple shell commands or functions
                for idx, line in enumerate(source_code.splitlines(), 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.endswith("() {") or line.startswith("function "):
                        func_name = line.replace("function ", "").split("(")[0].strip()
                        symbols.append({
                            "name": func_name,
                            "qualified_name": func_name,
                            "symbol_type": "SCRIPT_FUNCTION",
                            "content": line,
                            "start_line": idx,
                            "end_line": idx
                        })
            elif filename == "Dockerfile":
                matches = re.finditer(r"(FROM|RUN|COPY|CMD|EXPOSE|ENV|ENTRYPOINT|WORKDIR)\s+(.*)", source_code, re.IGNORECASE)
                for idx, match in enumerate(matches, 1):
                    inst = match.group(1).upper()
                    arg = match.group(2).strip()
                    symbols.append({
                        "name": f"{inst}_{idx}",
                        "qualified_name": f"{inst}_{idx}",
                        "symbol_type": "DOCKER_INSTRUCTION",
                        "content": f"{inst} {arg}",
                        "start_line": source_code[:match.start()].count("\n") + 1,
                        "end_line": source_code[:match.end()].count("\n") + 1
                    })
            elif filename == "Makefile":
                # Targets
                for idx, line in enumerate(source_code.splitlines(), 1):
                    if line.strip() and not line.startswith("\t") and ":" in line and not line.startswith("#"):
                        target = line.split(":")[0].strip()
                        if target and not target.startswith("."):
                            symbols.append({
                                "name": target,
                                "qualified_name": target,
                                "symbol_type": "MAKE_TARGET",
                                "content": line.strip(),
                                "start_line": idx,
                                "end_line": idx
                            })
            elif filename == ".gitignore":
                for idx, line in enumerate(source_code.splitlines(), 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    symbols.append({
                        "name": line,
                        "qualified_name": line,
                        "symbol_type": "IGNORE_RULE",
                        "content": line,
                        "start_line": idx,
                        "end_line": idx
                    })
            
            return {
                "type": "FLATFILE",
                "symbols": symbols,
                "raw_content": source_code
            }
        except Exception as e:
            print(f"[ERROR] Flatfile parsing failed for {file_path}: {e}")
            return FileParser._empty_result()