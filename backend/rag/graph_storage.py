# =========================================================
# GRAPH STORAGE
# =========================================================

import json

# =========================================================
# SAVE GRAPH
# =========================================================

def save_graph(

    graph,

    output_file

):

    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            graph,

            f,

            indent=4
        )

# =========================================================
# LOAD GRAPH
# =========================================================

def load_graph(

    graph_file

):

    with open(

        graph_file,

        "r",

        encoding="utf-8"

    ) as f:

        return json.load(f)
    