# =========================================================
# V2 GRAPH DATABASE MODULE (NETWORKX)
# =========================================================

import os
import json
import networkx as nx
from networkx.readwrite import json_graph

class GraphDatabase:
    """Manages the repository relationship graph using a NetworkX DiGraph."""
    
    def __init__(self):
        self.g = nx.DiGraph()
        
    def add_node(self, node_id: str, node_type: str, name: str, file_path: str, repo_name: str, **metadata):
        """Adds a node with structured attributes."""
        self.g.add_node(
            node_id,
            type=node_type,
            name=name,
            file_path=file_path,
            repo_name=repo_name,
            **metadata
        )
        
    def add_edge(self, source: str, target: str, relation: str):
        """Adds a directed edge representing code relationships."""
        # Ensure nodes exist
        if source not in self.g:
            self.g.add_node(source, type="UNKNOWN")
        if target not in self.g:
            self.g.add_node(target, type="UNKNOWN")
            
        self.g.add_edge(source, target, relation=relation)
        
    def save_to_json(self, output_path: str):
        """Serializes the NetworkX graph using standard JSON node-link format."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        data = json_graph.node_link_data(self.g)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[INFO] Saved NetworkX graph to {output_path} ({self.g.number_of_nodes()} nodes, {self.g.number_of_edges()} edges)")
        
    def load_from_json(self, input_path: str):
        """Deserializes the NetworkX graph from a node-link JSON file."""
        if not os.path.exists(input_path):
            print(f"[WARNING] Graph file not found at {input_path}. Starting with empty graph.")
            self.g = nx.DiGraph()
            return
            
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.g = json_graph.node_link_graph(data)
            print(f"[INFO] Loaded NetworkX graph from {input_path} ({self.g.number_of_nodes()} nodes, {self.g.number_of_edges()} edges)")
        except Exception as e:
            print(f"[ERROR] Failed to load NetworkX graph: {e}")
            self.g = nx.DiGraph()

    def get_node_info(self, node_id: str) -> dict:
        """Fetch node metadata."""
        if node_id in self.g:
            return self.g.nodes[node_id]
        return {}

    def get_related_neighbors(self, node_id: str, max_neighbors: int = 15) -> list:
        """Retrieves callers, callees, containers, imports, inherits, etc. dynamically."""
        neighbors = []
        if node_id not in self.g:
            return neighbors
            
        # 1. Successors (outgoing edges: calls, inherits, uses, contains)
        for succ in self.g.successors(node_id):
            edge_data = self.g.get_edge_data(node_id, succ)
            relation = edge_data.get("relation", "DEPENDS_ON")
            neighbors.append({
                "node_id": succ,
                "type": self.g.nodes[succ].get("type", "UNKNOWN"),
                "relation": relation,
                "direction": "out"
            })
            
        # 2. Predecessors (incoming edges: callers, subclasses, container file)
        for pred in self.g.predecessors(node_id):
            edge_data = self.g.get_edge_data(pred, node_id)
            relation = edge_data.get("relation", "DEPENDS_ON")
            neighbors.append({
                "node_id": pred,
                "type": self.g.nodes[pred].get("type", "UNKNOWN"),
                "relation": relation,
                "direction": "in"
            })
            
        return neighbors[:max_neighbors]

    def get_statistics(self) -> dict:
        """Calculate counts of nodes/edges by category."""
        stats = {
            "node_count": self.g.number_of_nodes(),
            "edge_count": self.g.number_of_edges(),
            "node_types": {},
            "edge_relations": {}
        }
        
        for _, ndata in self.g.nodes(data=True):
            ntype = ndata.get("type", "UNKNOWN")
            stats["node_types"][ntype] = stats["node_types"].get(ntype, 0) + 1
            
        for _, _, edata in self.g.edges(data=True):
            relation = edata.get("relation", "UNKNOWN")
            stats["edge_relations"][relation] = stats["edge_relations"].get(relation, 0) + 1
            
        return stats
