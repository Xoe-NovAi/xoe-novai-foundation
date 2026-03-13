# Vikunja Importer API Surface (v1.0.0)

- Summary: Lightweight REST interactions to push tasks, projects, and namespaces into Vikunja.
- Endpoints covered: POST /projects, POST /tasks, GET /projects (exists for idempotency tests), and batch-like structuring hints.
- Authentication: Bearer token via Authorization header.
- Error handling: basic retry/backoff patterns and idempotent checks where possible.

Notes
- This surface is designed for the v1.0.0 migration bundle; evolve as Vikunja API evolves.
