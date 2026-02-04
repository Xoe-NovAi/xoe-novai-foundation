Remediation Summary — 2026-01-28
================================

Snapshot of recent remediation work and notes for memory bank.

- Short summary: Applied safety & import-time fixes to reduce test/CI failures and gate unsafe operations.
- Key touched modules: `core/dependencies.py`, `core/vectorstore_shim.py`, `core/awq_quantizer.py`, `tests/conftest.py`.
- Test note: targeted circuit-breaker tests passed in Python 3.12 container (6 passed, 1 skipped).

Pointers:
- Briefing: internal_docs/dev/remediation_briefing.md
- Audit template: internal_docs/dev/pr_code_audit_template.md (created)
- Full stack audit (initial): internal_docs/dev/stack_audit_report.md

Audit tags: remediation, tests, faiss, onnxruntime, numpy, pybreaker, docker-python-3.12

Chronology: implemented fixes 2026-01-28 to address import-time NameError, heavy-binary imports, and pybreaker compatibility for tests.
