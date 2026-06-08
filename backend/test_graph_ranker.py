from rag.retrieval.graph_ranker import (
    apply_graph_boost
)

chunks = [

    {
        "qualified_name": "repo.create_user",
        "score": 0.8
    },

    {
        "qualified_name": "repo.save_user",
        "score": 0.5
    }
]

expanded_nodes = {

    "repo.save_user"
}

results = apply_graph_boost(

    chunks,

    expanded_nodes
)

print()

print(
    "GRAPH RANKING"
)

for item in results:

    print(

        item["qualified_name"],

        item["graph_score"]
    )