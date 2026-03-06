import os
import subprocess
import sys


def test_smoke_import_app():
    """Smoke test: ensure `app` package imports under PYTHONPATH=./app using current Python."""
    env = os.environ.copy()
    # Ensure the app package is importable by tests using the app/ folder
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + (":" if env.get("PYTHONPATH") else "") + os.path.abspath("./app")

    # Run a small subprocess to verify import in a fresh interpreter
    code = "import importlib; importlib.import_module('XNAi_rag_app'); print('OK')"
    completed = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)

    if completed.returncode != 0:
        raise AssertionError(
            f"smoke-import failed (returncode={completed.returncode})\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )

    assert "OK" in completed.stdout
