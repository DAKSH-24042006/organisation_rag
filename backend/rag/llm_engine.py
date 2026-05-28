# =========================================================
# llm_engine.py
# =========================================================

import requests
import json
import time

from rag.config import OLLAMA_MODEL

# =========================================================
# OLLAMA CONFIG
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

REQUEST_TIMEOUT = 300

MAX_RETRIES = 3

TEMPERATURE = 0.2

TOP_P = 0.9

NUM_PREDICT = 4096

# =========================================================
# CLEAN RESPONSE
# =========================================================

def clean_response(text):

    if text is None:
        return ""

    text = text.strip()

    return text

# =========================================================
# BUILD PAYLOAD
# =========================================================

def build_payload(

    prompt,
    system_prompt=None
):

    payload = {

        "model": OLLAMA_MODEL,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": TEMPERATURE,

            "top_p": TOP_P,

            "num_predict": NUM_PREDICT
        }
    }

    # =====================================================
    # OPTIONAL SYSTEM PROMPT
    # =====================================================

    if system_prompt:

        payload["system"] = system_prompt

    return payload

# =========================================================
# VALIDATE RESPONSE
# =========================================================

def validate_response(response_json):

    if "response" not in response_json:

        raise ValueError(
            "Invalid LLM response structure."
        )

    return response_json["response"]

# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate_llm_response(

    prompt,
    system_prompt=None
):

    payload = build_payload(

        prompt=prompt,

        system_prompt=system_prompt
    )

    retry_count = 0

    while retry_count < MAX_RETRIES:

        try:

            print(
                f"\n[LLM] Generating using: "
                f"{OLLAMA_MODEL}"
            )

            response = requests.post(

                OLLAMA_URL,

                json=payload,

                timeout=REQUEST_TIMEOUT
            )

            # =============================================
            # HTTP VALIDATION
            # =============================================

            response.raise_for_status()

            # =============================================
            # JSON PARSE
            # =============================================

            result = response.json()

            generated_text = validate_response(
                result
            )

            generated_text = clean_response(
                generated_text
            )

            print(
                "\n[LLM] Generation complete."
            )

            return generated_text

        except requests.exceptions.Timeout:

            retry_count += 1

            print(
                f"\n[LLM ERROR] Timeout. "
                f"Retry {retry_count}/"
                f"{MAX_RETRIES}"
            )

            time.sleep(2)

        except requests.exceptions.ConnectionError:

            raise ConnectionError(

                "\nCould not connect to Ollama.\n"

                "Make sure Ollama is running:\n"

                "ollama serve"
            )

        except requests.exceptions.HTTPError as e:

            raise RuntimeError(

                f"\nHTTP Error: {e}"
            )

        except json.JSONDecodeError:

            raise ValueError(

                "\nFailed to parse Ollama JSON response."
            )

        except Exception as e:

            raise RuntimeError(

                f"\nUnexpected LLM Error: {e}"
            )

    raise RuntimeError(

        "\nLLM generation failed after retries."
    )

# =========================================================
# STREAMING GENERATION (FUTURE READY)
# =========================================================

def stream_llm_response(

    prompt,
    system_prompt=None
):

    payload = build_payload(

        prompt=prompt,

        system_prompt=system_prompt
    )

    payload["stream"] = True

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            stream=True,

            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if line:

                decoded = json.loads(

                    line.decode("utf-8")
                )

                token = decoded.get(
                    "response",
                    ""
                )

                yield token

    except Exception as e:

        raise RuntimeError(

            f"\nStreaming Error: {e}"
        )

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    system_prompt = """

You are an enterprise coding assistant.

Follow:
- repository architecture
- engineering conventions
- clean coding standards
- reusable utilities
"""

    user_prompt = """

Create JWT authentication middleware
with Redis session storage.
"""

    print("\n" + "=" * 80)

    print("TESTING LLM ENGINE")

    print("=" * 80)

    result = generate_llm_response(

        prompt=user_prompt,

        system_prompt=system_prompt
    )

    print("\n" + "=" * 80)

    print("LLM RESPONSE")

    print("=" * 80)

    print(result)