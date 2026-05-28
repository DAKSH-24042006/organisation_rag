# =========================================================
# llm_semantic_analyzer.py
# =========================================================

import json
import requests

from rag.config import OLLAMA_MODEL

# =========================================================
# OLLAMA URL
# =========================================================

OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)

# =========================================================
# BUILD PROMPT
# =========================================================

def build_semantic_prompt(code):

    return f"""

You are an expert software architect.

Analyze the following code.

Determine:

1. Business role
2. Semantic tags
3. Workflow purpose
4. Architecture role
5. Security relevance
6. API relevance
7. Database relevance
8. Frontend/backend classification
9. Dependencies used
10. Short summary

Return ONLY valid JSON.

Example:

{{
  "business_role": "authentication_service",
  "semantic_tags": [
    "authentication",
    "security",
    "react"
  ],
  "workflows": [
    "login_flow",
    "session_restore"
  ],
  "architecture_role":
  "frontend_context_provider",

  "summary":
  "Handles authentication state.",

  "security_relevance": true,
  "api_relevance": true,
  "database_relevance": false,
  "frontend": true,
  "backend": false
}}

Code:

{code[:4000]}
"""

# =========================================================
# FALLBACK
# =========================================================

def fallback_response():

    return {

        "business_role":
        "general_service",

        "semantic_tags": [],

        "workflows": [],

        "architecture_role":
        "general_component",

        "summary":
        "",

        "security_relevance":
        False,

        "api_relevance":
        False,

        "database_relevance":
        False,

        "frontend":
        False,

        "backend":
        False
    }

# =========================================================
# ANALYZE CODE
# =========================================================

def llm_analyze_code_semantics(code):

    try:

        prompt = build_semantic_prompt(
            code
        )

        payload = {

            "model":
            OLLAMA_MODEL,

            "prompt":
            prompt,

            "stream":
            False
        }

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=120
        )

        result = response.json()

        response_text = result.get(
            "response",
            ""
        )

        # =============================================
        # EXTRACT JSON
        # =============================================

        start = response_text.find("{")

        end = response_text.rfind("}")

        if start == -1 or end == -1:

            return fallback_response()

        json_text = response_text[
            start:end + 1
        ]

        semantic_data = json.loads(
            json_text
        )

        return semantic_data

    except Exception as e:

        print(
            f"[LLM ANALYZER ERROR] {e}"
        )

        return fallback_response()

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_code = '''

const login = async () => {

    const response =
        await authApi.login()

    localStorage.setItem(
        "token",
        response.token
    )
}

'''

    result = llm_analyze_code_semantics(
        sample_code
    )

    print(result)