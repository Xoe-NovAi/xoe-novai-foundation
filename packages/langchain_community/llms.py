"""Minimal shim for `langchain_community.llms` to satisfy imports during unit tests.

This provides a lightweight `LlamaCpp` stub that raises a clear error if used at runtime.
For full integration tests, install the real `langchain-community` package and run in the container.
"""
class LlamaCpp:
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "LlamaCpp shim: full LlamaCpp implementation is not available in unit test shims."
            " Install langchain-community or run integration tests in the container."
        )

__all__ = ["LlamaCpp"]
