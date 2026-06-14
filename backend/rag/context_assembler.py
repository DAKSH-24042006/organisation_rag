# =========================================================
# V2 CONTEXT ASSEMBLER MODULE
# =========================================================

import os
from rag.config import DEFAULT_REPO_PATH, REPOSITORIES

class ContextAssembler:
    """Structures retrieved evidence into a clean, contextual prompt context for the LLM."""
    
    @staticmethod
    def assemble_context(retrieval_data: dict) -> str:
        query_type = retrieval_data.get("query_type", "GENERAL")
        results = retrieval_data.get("results", [])
        query = retrieval_data.get("query", "")
        
        if not results:
            return "No matching source code or context found in the repository."
            
        # 1. FILE RECOVERY Bypass
        if query_type == "FILE_RECOVERY":
            best_match = None
            if query:
                q_lower = query.lower()
                for r in results:
                    if r.get("type") == "FILE":
                        filename = os.path.basename(r.get("path", "")).lower()
                        name_without_ext = os.path.splitext(filename)[0]
                        if filename in q_lower or (name_without_ext and name_without_ext in q_lower):
                            best_match = r
                            break
                            
            if not best_match:
                for r in results:
                    if r.get("type") == "FILE":
                        best_match = r
                        break
                        
            if best_match:
                rel_path = best_match.get("path")
                repo_name = best_match.get("repo_name")
                repo_path = DEFAULT_REPO_PATH
                if repo_name:
                    for repo in REPOSITORIES:
                        if repo.get("name") == repo_name:
                            repo_path = repo.get("path")
                            break
                abs_path = os.path.join(repo_path or "", rel_path or "")
                if os.path.exists(abs_path):
                    try:
                        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                            full_code = f.read()
                        return f"--- FILE CONTENT OF {rel_path} ---\n{full_code}"
                    except Exception:
                        pass
                        
        # 2. Assemble Structured Context Package
        context_parts = []
        
        # Section A: Header Package Metadata
        context_parts.append("==========================================================")
        context_parts.append("📦 RAG CONTEXT PACKAGE")
        context_parts.append(f"Intent Classification: {query_type}")
        context_parts.append("==========================================================\n")
        
        # Section B: Mapped Dependency/Call Trace Paths
        relationships = []
        for r in results:
            rels = r.get("graph_relationships", [])
            if rels:
                relationships.extend(rels)
                
        unique_rels = list(dict.fromkeys(relationships))
        if unique_rels:
            context_parts.append("🕸️ [ACTIVE CALL & DEPENDENCY PATH MAP]")
            for rel in unique_rels[:15]:
                context_parts.append(f"  - {rel}")
            context_parts.append("")
            
        # Section C: Configuration & Database Schemas
        config_chunks = [r for r in results if r.get("type") in {"CONFIG", "DATABASE"}]
        if config_chunks:
            context_parts.append("⚙️ [CONFIGURATION & DATABASE SCHEMAS]")
            for c in config_chunks:
                context_parts.append(f"\n--- File: {c.get('path')} | Type: {c.get('type')} ---")
                context_parts.append(c.get("content", ""))
            context_parts.append("\n")
            
        # Section D: Documentation Content (including Repository Map)
        doc_chunks = [r for r in results if r.get("type") in {"DOCS", "DOC"}]
        if doc_chunks:
            context_parts.append("📖 [DOCUMENTATION & BLUEPRINT CONTENT]")
            for d in doc_chunks:
                context_parts.append(f"\n--- Title: {d.get('name')} | Source: {d.get('path')} ---")
                context_parts.append(d.get("content", ""))
            context_parts.append("\n")
            
        # Section E: Source Code Evidence (Grouped & Deduplicated)
        code_chunks = [r for r in results if r.get("type") not in {"CONFIG", "DATABASE", "DOCS", "DOC"}]
        if code_chunks:
            context_parts.append("💻 [SOURCE CODE EVIDENCE]")
            
            # Group by file path
            by_file = {}
            for chunk in code_chunks:
                fpath = chunk.get("path", "Unknown File")
                if fpath not in by_file:
                    by_file[fpath] = []
                by_file[fpath].append(chunk)
                
            # Deduplicate and merge overlapping intervals within each file
            for fpath, chunks in by_file.items():
                context_parts.append(f"\n==========================================")
                context_parts.append(f"FILE: {fpath}")
                context_parts.append(f"==========================================")
                
                # Fetch full file contents if possible for accurate line slicing
                repo_name = chunks[0].get("repo_name")
                repo_path = DEFAULT_REPO_PATH
                if repo_name:
                    for repo in REPOSITORIES:
                        if repo.get("name") == repo_name:
                            repo_path = repo.get("path")
                            break
                            
                abs_path = os.path.join(repo_path or "", fpath)
                file_lines = []
                if os.path.exists(abs_path):
                    try:
                        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_lines = f.read().splitlines()
                    except Exception:
                        pass
                
                # Extract line intervals (start_line, end_line) - note line numbers are 1-indexed
                intervals = []
                for c in chunks:
                    start = max(1, c.get("start_line", 1))
                    end = c.get("end_line", start)
                    intervals.append((start, end, c))
                    
                # Merge intervals
                intervals.sort(key=lambda x: x[0])
                merged = []
                if intervals:
                    curr_start, curr_end = intervals[0][0], intervals[0][1]
                    for start, end, c in intervals[1:]:
                        if start <= curr_end + 3:  # merge if overlapping or within 3 lines
                            curr_end = max(curr_end, end)
                        else:
                            merged.append((curr_start, curr_end))
                            curr_start, curr_end = start, end
                    merged.append((curr_start, curr_end))
                    
                # Print merged segments
                for start, end in merged:
                    context_parts.append(f"\n--- Code Segment (Lines {start}-{end}) ---")
                    
                    if file_lines and start <= len(file_lines):
                        # Slice from physical file
                        segment_lines = file_lines[start-1:end]
                        context_parts.append("\n".join(segment_lines))
                    else:
                        # Fallback to reconstructing from chunks content
                        segment_chunks = [c for s, e, c in intervals if s >= start and e <= end]
                        if segment_chunks:
                            segment_chunks.sort(key=lambda x: x.get("start_line", 0))
                            context_parts.append("\n".join([sc.get("content", "") for sc in segment_chunks]))
                        else:
                            # Fallback to the first chunk's content
                            context_parts.append(chunks[0].get("content", ""))
                            
        return "\n".join(context_parts)
