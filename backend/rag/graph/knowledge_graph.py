# =========================================================
# KNOWLEDGE GRAPH
# =========================================================

class KnowledgeGraph:

    def __init__(self):

        self.nodes = {}

        self.edges = []

    # =====================================================
    # ADD NODE
    # =====================================================

    def add_node(

        self,
        node_id,
        node_type,
        **metadata

    ):

        self.nodes[node_id] = {

            "id": node_id,

            "type": node_type,

            **metadata
        }

    # =====================================================
    # ADD EDGE
    # =====================================================

    def add_edge(

        self,
        source,
        target,
        relation

    ):

        self.edges.append({

            "source": source,

            "target": target,

            "relation": relation
        })

    # =====================================================
    # GET NODE
    # =====================================================

    def get_node(

        self,
        node_id

    ):

        return self.nodes.get(
            node_id
        )

    # =====================================================
    # GET NEIGHBORS
    # =====================================================

    def get_neighbors(

        self,
        node_id

    ):

        neighbors = []

        for edge in self.edges:

            if edge["source"] == node_id:

                neighbors.append({

                    "node": edge["target"],

                    "relation": edge["relation"]
                })

        return neighbors

    # =====================================================
    # STATS
    # =====================================================

    def num_nodes(self):

        return len(
            self.nodes
        )

    def num_edges(self):

        return len(
            self.edges
        )

    # =====================================================
    # DEBUG
    # =====================================================

    def summary(self):

        return {

            "nodes": self.num_nodes(),

            "edges": self.num_edges()
        }