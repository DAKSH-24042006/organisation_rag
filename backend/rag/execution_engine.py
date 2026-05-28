# =========================================================
# execution_engine.py
# =========================================================

import subprocess
import tempfile
import os

# =========================================================
# EXECUTE PYTHON CODE
# =========================================================

def execute_python_code(code):

    with tempfile.NamedTemporaryFile(

        suffix=".py",

        delete=False,

        mode="w",

        encoding="utf-8"

    ) as temp_file:

        temp_file.write(code)

        temp_path = temp_file.name

    try:

        result = subprocess.run(

            ["python", temp_path],

            capture_output=True,

            text=True,

            timeout=20
        )

        return {

            "stdout":
            result.stdout,

            "stderr":
            result.stderr,

            "returncode":
            result.returncode
        }

    except Exception as e:

        return {

            "error":
            str(e)
        }

    finally:

        if os.path.exists(temp_path):

            os.remove(temp_path)

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    code = """

print("Hello World")
"""

    result = execute_python_code(
        code
    )

    print(result)