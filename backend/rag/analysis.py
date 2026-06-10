# =========================================================
# V2 REPOSITORY STATIC ANALYSIS MODULE
# =========================================================

import os
import json
from rag.config import GRAPH_PATH, INDEX_PATH
from rag.graph_database import GraphDatabase

class RepositoryAnalyzer:
    """Performs global analysis of the repository using index and NetworkX dependency graph."""
    
    @staticmethod
    def analyze_repository() -> dict:
        graph_path = GRAPH_PATH
        index_path = INDEX_PATH
        
        analysis = {
            "statistics": {
                "files": 0,
                "classes": 0,
                "functions": 0,
                "endpoints": 0,
                "tables": 0,
                "configs": 0
            },
            "components": {},
            "endpoints_list": [],
            "tables_list": [],
            "configs_list": [],
            "dependencies": []
        }
        
        # 1. Load Graph
        graph = GraphDatabase()
        if not os.path.exists(graph_path):
            return analysis
        graph.load_from_json(graph_path)
        
        # 2. Extract Statistics and Lists
        for node_id, ndata in graph.g.nodes(data=True):
            ntype = ndata.get("type", "UNKNOWN")
            file_path = ndata.get("file_path", "")
            
            # Group components by parent folders
            if file_path:
                parts = file_path.split("/")
                if len(parts) > 1:
                    dir_name = parts[0]
                    analysis["components"][dir_name] = analysis["components"].get(dir_name, 0) + 1
                    
            if ntype == "FILE":
                analysis["statistics"]["files"] += 1
            elif ntype == "CLASS":
                analysis["statistics"]["classes"] += 1
            elif ntype == "FUNCTION":
                analysis["statistics"]["functions"] += 1
                
                # Check if it's an API Route
                if ndata.get("component_type") == "API_ROUTE" or ndata.get("route"):
                    analysis["statistics"]["endpoints"] += 1
                    analysis["endpoints_list"].append({
                        "id": node_id,
                        "name": ndata.get("name"),
                        "method": ndata.get("http_method", "GET"),
                        "route": ndata.get("route"),
                        "file": file_path
                    })
                    
            elif ntype in {"SQL_TABLE", "DATABASE"}:
                analysis["statistics"]["tables"] += 1
                analysis["tables_list"].append({
                    "id": node_id,
                    "name": ndata.get("name"),
                    "file": file_path
                })
            elif ntype in {"CONFIG", "CONFIG_KEY", "ENV_VAR"}:
                analysis["statistics"]["configs"] += 1
                analysis["configs_list"].append({
                    "id": node_id,
                    "name": ndata.get("name"),
                    "type": ntype,
                    "file": file_path
                })

        # 3. Extract Core Dependencies (Imports and Call structures)
        for u, v, edata in graph.g.edges(data=True):
            relation = edata.get("relation", "")
            if relation == "imports":
                analysis["dependencies"].append({
                    "source": u,
                    "target": v,
                    "type": "IMPORT"
                })
            elif relation == "calls":
                # Only log high-level calls across files to avoid listing every tiny line call
                u_file = graph.g.nodes[u].get("file_path", "")
                v_file = graph.g.nodes[v].get("file_path", "")
                if u_file and v_file and u_file != v_file:
                    analysis["dependencies"].append({
                        "source": u.split("::")[-1],
                        "target": v.split("::")[-1],
                        "type": "CALL"
                    })
                    
        return analysis

    @staticmethod
    def generate_markdown_summary(analysis: dict) -> str:
        """Generates a premium, styled markdown report from analysis data."""
        stats = analysis["statistics"]
        
        md = []
        md.append("# 📊 Repository Static Architecture Summary\n")
        
        # Statistics Table
        md.append("## 📈 Repository Statistics")
        md.append("| Metric | Count |")
        md.append("| :--- | :--- |")
        md.append(f"| 📁 Source Files | {stats['files']} |")
        md.append(f"| 📦 Classes | {stats['classes']} |")
        md.append(f"| ⚙️ Functions/Methods | {stats['functions']} |")
        md.append(f"| 🌐 API Endpoints | {stats['endpoints']} |")
        md.append(f"| 🗄️ Database Tables | {stats['tables']} |")
        md.append(f"| ⚙️ Config Elements | {stats['configs']} |\n")
        
        # Major Components
        md.append("## 📂 Major Components")
        if analysis["components"]:
            for folder, count in sorted(analysis["components"].items()):
                md.append(f"- **`{folder}/`**: Contains {count} code/structural elements.")
        else:
            md.append("No distinct folder structure components identified.")
        md.append("")
        
        # APIs / Endpoints
        md.append("## 🌐 API Routes & Services")
        if analysis["endpoints_list"]:
            md.append("| Method | Route | Function / Service | File |")
            md.append("| :--- | :--- | :--- | :--- |")
            for ep in analysis["endpoints_list"]:
                md.append(f"| `{ep['method']}` | `{ep['route']}` | `{ep['name']}` | `{ep['file']}` |")
        else:
            md.append("No API endpoints or routes detected in this repository.")
        md.append("")
        
        # Database Tables
        md.append("## 🗄️ Database Tables & Schemas")
        if analysis["tables_list"]:
            for t in analysis["tables_list"]:
                md.append(f"- **`{t['name']}`** (Declared in `{t['file']}`)")
        else:
            md.append("No database table definitions parsed.")
        md.append("")
        
        # Configuration
        md.append("## ⚙️ Configuration Files & Settings")
        configs_seen = {c["file"] for c in analysis["configs_list"]}
        if configs_seen:
            for conf_file in sorted(configs_seen):
                md.append(f"- **`{conf_file}`**")
        else:
            md.append("No config files or environment variables identified.")
        md.append("")
        
        # Dependencies overview
        md.append("## 🕸️ Core Module Dependency Flow")
        imports = [d for d in analysis["dependencies"] if d["type"] == "IMPORT"]
        if imports:
            md.append("The following file import relationships are mapped in the graph:")
            for imp in imports[:15]:  # limit to top 15 imports
                md.append(f"- `{imp['source']}` ➡️ imports ➡️ `{imp['target']}`")
        else:
            md.append("No cross-file import relationships mapped.")
            
        return "\n".join(md)
