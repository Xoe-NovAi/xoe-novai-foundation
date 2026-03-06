# Minimal shim for langchain_community.llms.LlamaCpp used in tests
# This avoids installing heavy langchain-community package during local test runs.

class LlamaCpp:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("LlamaCpp shim: LlamaCpp model is not available in this test shim. Use integration tests in container or install langchain-community package.")

__all__ = ["LlamaCpp"]
