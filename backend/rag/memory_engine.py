# =========================================================
# memory_engine.py
# =========================================================

import json
import os

# =========================================================
# MEMORY FILE
# =========================================================

MEMORY_FILE = "data/agent_memory.json"

# =========================================================
# LOAD MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(
        MEMORY_FILE
    ):

        return []

    with open(

        MEMORY_FILE,

        "r",

        encoding="utf-8"

    ) as f:

        return json.load(f)

# =========================================================
# SAVE MEMORY
# =========================================================

def save_memory(memory):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(

        MEMORY_FILE,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            memory,

            f,

            indent=2
        )

# =========================================================
# STORE INTERACTION
# =========================================================

def store_interaction(

    query,
    response,
    workflow_context
):

    memory = load_memory()

    memory.append({

        "query":
        query,

        "response":
        response,

        "workflow_context":
        workflow_context
    })

    save_memory(memory)

# =========================================================
# GET RECENT MEMORY
# =========================================================

def get_recent_memory(limit=5):

    memory = load_memory()

    return memory[-limit:]

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    store_interaction(

        "Generate JWT auth",

        "Generated code...",

        "Auth workflow"
    )

    print(

        get_recent_memory()
    )