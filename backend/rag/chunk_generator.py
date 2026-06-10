# =========================================================
# V2 CHUNK GENERATOR MODULE
# =========================================================

import os

class ChunkGenerator:
    """Groups parsed symbols and content into rich, non-trivial chunks."""
    
    @staticmethod
    def generate_chunks(symbols: list, file_path: str, relative_path: str, file_type: str, raw_content: str, repo_name: str) -> list:
        chunks = []
        filename = os.path.basename(file_path)
        
        # 1. Full File Chunk (High-level Context)
        # Always create a full file chunk so the file exists in the index
        if raw_content.strip():
            chunks.append({
                "id": relative_path,  # stable ID for the file itself
                "repo_name": repo_name,
                "type": "FILE",
                "name": filename,
                "qualified_name": relative_path,
                "file": filename,
                "path": relative_path,
                "start_line": 1,
                "end_line": len(raw_content.splitlines()),
                "content": raw_content[:4000],  # cap to prevent huge context,
                "embedding_text": f"File: {relative_path}\nRepository: {repo_name}\nContent:\n{raw_content[:2000]}"
            })
            
        # 2. Config Chunks (Grouped)
        # Avoid creating 100s of tiny 20-character chunks. Group them by sections or file.
        if file_type == "CONFIG":
            config_lines = []
            for s in symbols:
                config_lines.append(f"{s['qualified_name']} = {s['content']}")
                
            if config_lines:
                config_summary = "\n".join(config_lines)
                chunks.append({
                    "id": f"{relative_path}::CONFIG_SUMMARY",
                    "repo_name": repo_name,
                    "type": "CONFIG",
                    "name": filename,
                    "qualified_name": f"{relative_path}::CONFIG_SUMMARY",
                    "file": filename,
                    "path": relative_path,
                    "start_line": 1,
                    "end_line": len(raw_content.splitlines()) or 1,
                    "content": raw_content,
                    "embedding_text": f"Configuration File: {relative_path}\nSettings:\n{config_summary[:2000]}"
                })
            return chunks

        # 3. Document / Markdown Chunks
        if file_type == "DOCUMENTATION":
            for s in symbols:
                # Filter out extremely short headers without content
                content = s.get("content", "").strip()
                if len(content) < 30:
                    continue
                chunks.append({
                    "id": s["id"],
                    "repo_name": repo_name,
                    "type": "DOCS",
                    "name": s["name"],
                    "qualified_name": s["qualified_name"],
                    "file": filename,
                    "path": relative_path,
                    "start_line": s["start_line"],
                    "end_line": s["end_line"],
                    "content": content,
                    "embedding_text": f"Documentation Section in '{relative_path}' -> {s['name']}\nContent:\n{content[:2000]}"
                })
            return chunks

        # 4. Code & Database Symbols
        for s in symbols:
            stype = s["symbol_type"]
            content = s.get("content", "").strip()
            
            # Avoid tiny, useless chunks (e.g. empty constructors, minor getters/imports/calls)
            # Imports and calls are used to build the graph, but they shouldn't be individual vector chunks!
            if stype in {"IMPORT", "CALL"}:
                continue
                
            # Filter extremely short function definitions (e.g. pass, simple returns) to avoid clutter
            if stype == "FUNCTION" and (len(content) < 80 or content.count("\n") < 2):
                continue
                
            chunk_type = "SYMBOL"
            if stype == "SQL_TABLE":
                chunk_type = "DATABASE"
            elif stype == "CLASS":
                chunk_type = "SYMBOL"
                
            chunks.append({
                "id": s["id"],
                "repo_name": repo_name,
                "type": chunk_type,
                "name": s["name"],
                "qualified_name": s["qualified_name"],
                "file": filename,
                "path": relative_path,
                "start_line": s["start_line"],
                "end_line": s["end_line"],
                "content": content,
                "framework": s.get("framework"),
                "component_type": s.get("component_type"),
                "http_method": s.get("http_method"),
                "route": s.get("route"),
                "is_async": s.get("is_async", False),
                "embedding_text": f"Repository: {repo_name}\nFile: {relative_path}\nType: {stype} ({s.get('component_type', 'Code Entity')})\nName: {s['qualified_name']}\nCode:\n{content[:2000]}"
            })
            
        return chunks