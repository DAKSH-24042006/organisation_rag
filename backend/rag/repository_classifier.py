# =========================================================
# repository_classifier.py
# =========================================================

import json
from collections import defaultdict

# =========================================================
# LOAD CHUNKS
# =========================================================

with open(

    "data/repository_index.json",

    "r",

    encoding="utf-8"

) as f:

    code_chunks = json.load(f)

# =========================================================
# CLASSIFY REPOSITORY
# =========================================================

def classify_repository():

    classification = {

        "languages":
        defaultdict(int),

        "business_roles":
        defaultdict(int),

        "semantic_tags":
        defaultdict(int)
    }

    for chunk in code_chunks:

        language = chunk.get(
            "language",
            "unknown"
        )

        classification[
            "languages"
        ][language] += 1

        role = chunk.get(
            "business_role",
            "general_service"
        )

        classification[
            "business_roles"
        ][role] += 1

        tags = chunk.get(
            "semantic_tags",
            []
        )

        for tag in tags:

            classification[
                "semantic_tags"
            ][tag] += 1

    return classification

# =========================================================
# DISPLAY CLASSIFICATION
# =========================================================

def display_classification():

    classification = classify_repository()

    print("\n" + "=" * 80)

    print("REPOSITORY CLASSIFICATION")

    print("=" * 80)

    print("\nLANGUAGES\n")

    for k, v in classification[
        "languages"
    ].items():

        print(f"{k}: {v}")

    print("\nBUSINESS ROLES\n")

    for k, v in classification[
        "business_roles"
    ].items():

        print(f"{k}: {v}")

    print("\nSEMANTIC TAGS\n")

    for k, v in classification[
        "semantic_tags"
    ].items():

        print(f"{k}: {v}")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    display_classification()