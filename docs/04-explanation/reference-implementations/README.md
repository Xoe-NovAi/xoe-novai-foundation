# Reference Implementations: The Golden Standards
**Status**: Elite Hardened
**Purpose**: Executable logic for core sovereign services.

These Python implementations represent the production-ready logic for Xoe-NovAi's security and sovereignty layers. Use these as the primary reference when implementing or auditing these services.

## 🛡️ [IAM Service (Zero-Trust)](iam-reference.py)
- **Logic**: RS256 JWT-based authentication.
- **Pattern**: SQLite WAL persistence with 256MB MMAP.
- **Goal**: Zero-trust identity management.

## 🏷️ [TextSeal (C2PA Watermarking)](textseal-reference.py)
- **Logic**: Cryptographic content provenance.
- **Pattern**: Unicode homoglyph and zero-width steganography.
- **Goal**: Verifiable AI content sovereignty.
