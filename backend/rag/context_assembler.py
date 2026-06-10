# =========================================================
# V2 CONTEXT ASSEMBLER MODULE
# =========================================================

class ContextAssembler:
    """Structures retrieved evidence into a clean, contextual prompt context for the LLM."""
    
    @staticmethod
    def assemble_context(retrieval_data: dict) -> str:
        query_type = retrieval_data.get("query_type", "GENERAL")
        results = retrieval_data.get("results", [])
        
        if not results:
            return "No matching source code or context found in the repository."
            
        if query_type == "FILE_RECOVERY":
            import os
            from rag.config import DEFAULT_REPO_PATH
            for r in results:
                if r.get("type") == "FILE":
                    rel_path = r.get("path")
                    abs_path = os.path.join(DEFAULT_REPO_PATH, rel_path)
                    if os.path.exists(abs_path):
                        try:
                            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                                full_code = f.read()
                            return f"--- FILE CONTENT OF {rel_path} ---\n{full_code}"
                        except Exception as e:
                            pass
                            
        context_parts = []
        
        # 1. Header Metadata
        context_parts.append(f"--- QUERY INTENT CLASSIFICATION: {query_type} ---")
        
        # 2. Retrieved File List
        files_seen = set()
        for r in results:
            path = r.get("path")
            if path:
                files_seen.add(path)
                
        context_parts.append("\n[RELEVANT REPOSITORY FILES]")
        for f in sorted(files_seen):
            context_parts.append(f"- {f}")
            
        # 3. Configuration & Database Tables (if any)
        config_chunks = [r for r in results if r.get("type") in {"CONFIG", "DATABASE"}]
        if config_chunks:
            context_parts.append("\n[CONFIGURATION & DATABASE DEFINITIONS]")
            for c in config_chunks:
                context_parts.append(f"\n--- File: {c.get('path')} | Type: {c.get('type')} ---")
                context_parts.append(c.get("content", ""))
                
        # 4. Graph Dependencies (if any)
        # Extract the graph relationships attached to retrieval results
        relationships = []
        for r in results:
            rels = r.get("graph_relationships", [])
            if rels:
                relationships.extend(rels)
                
        # Unique list
        unique_rels = list(dict.fromkeys(relationships))
        if unique_rels:
            context_parts.append("\n[CODE STRUCTURE DEPENDENCY MAP]")
            for rel in unique_rels[:15]:  # limit to top 15 edges
                context_parts.append(f"  {rel}")
                
        # 5. Code Evidence (Grouped by file to keep it readable and cohesive)
        code_chunks = [r for r in results if r.get("type") not in {"CONFIG", "DATABASE", "DOCS"}]
        doc_chunks = [r for r in results if r.get("type") == "DOCS"]
        
        if doc_chunks:
            context_parts.append("\n[DOCUMENTATION CONTENT]")
            for d in doc_chunks:
                context_parts.append(f"\n--- Section: {d.get('name')} in {d.get('path')} ---")
                context_parts.append(d.get("content", ""))
                
        if code_chunks:
            context_parts.append("\n[SOURCE CODE EVIDENCE]")
            
            # Group by file path
            by_file = {}
            for chunk in code_chunks:
                fpath = chunk.get("path", "Unknown File")
                if fpath not in by_file:
                    by_file[fpath] = []
                by_file[fpath].append(chunk)
                
            # Iterate through grouped files
            for fpath, chunks in by_file.items():
                context_parts.append(f"\n==========================================")
                context_parts.append(f"FILE: {fpath}")
                context_parts.append(f"==========================================")
                
                # Sort chunks by start line to read top-to-bottom
                chunks.sort(key=lambda x: x.get("start_line", 0))
                
                for c in chunks:
                    name = c.get("name")
                    stype = c.get("type")
                    s_line = c.get("start_line", 1)
                    e_line = c.get("end_line", 1)
                    code = c.get("content", "")
                    
                    context_parts.append(f"\n--- Entity: {name} (Lines {s_line}-{e_line}) ---")
                    context_parts.append(code)
                    
        return "\n".join(context_parts)
