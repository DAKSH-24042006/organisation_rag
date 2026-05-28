# =========================================================
# self_reflection.py
# =========================================================

# =========================================================
# CHECK ARCHITECTURE
# =========================================================

def check_architecture(response):

    score = 0

    feedback = []

    if "class" in response:

        score += 1

    if "try:" in response:

        score += 1

    if "except" in response:

        score += 1

    if "import" in response:

        score += 1

    if score < 2:

        feedback.append(

            "Code may lack proper structure."
        )

    return {

        "score":
        score,

        "feedback":
        feedback
    }

# =========================================================
# CHECK SECURITY
# =========================================================

def check_security(response):

    feedback = []

    if "jwt" in response.lower():

        if "secret" not in response.lower():

            feedback.append(

                "JWT secret handling missing."
            )

    return feedback

# =========================================================
# SELF REFLECTION
# =========================================================

def reflect_on_generation(response):

    architecture_check = (

        check_architecture(response)
    )

    security_feedback = (

        check_security(response)
    )

    return {

        "architecture":
        architecture_check,

        "security_feedback":
        security_feedback
    }

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    response = """

import jwt

def login():
    pass
"""

    print(

        reflect_on_generation(
            response
        )
    )