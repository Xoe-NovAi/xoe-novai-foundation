---
applyTo: ["app/XNAi_rag_app/api/**/*.py", "app/XNAi_rag_app/schemas/**/*.py"]
---

# API Instructions

Follow these standards for all FastAPI/REST developments:
1.  **Unified Exceptions**: Use the `XNAiException` base class.
2.  **Pydantic V2**: Use strict typing and validation.
3.  **JSON Logging**: Include `trace_id` and `span_id` in all error responses.
4.  **Hardware Awareness**: APIs must be asynchronous to prevent CPU stalls during I/O.
