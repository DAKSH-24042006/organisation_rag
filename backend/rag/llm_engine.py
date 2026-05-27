import requests

from rag.config import OLLAMA_MODEL

# =========================================================
# LLM ENGINE
# =========================================================

def generate_llm_response(prompt):

    url = "http://localhost:11434/api/generate"

    payload = {

        "model": OLLAMA_MODEL,

        "prompt": prompt,

        "stream": False
    }

    response = requests.post(
        url,
        json=payload
    )

    result = response.json()

    return result["response"]