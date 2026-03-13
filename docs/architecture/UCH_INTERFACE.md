# 🔱 Unified Crystal Hash (UCH) Interface
[AP:memory_bank/ALETHIA_REGISTRY.md#L15] (SOS-F7: ZLV/Techne)

## Overview
The Unified Crystal Hash (UCH) protocol provides a language-agnostic mechanism for verifying the **functional rigidity** of source code. Unlike traditional file hashes (MD5/SHA), UCH focuses on the Abstract Syntax Tree (AST), ensuring that changes to non-functional elements (comments, docstrings, formatting, type hints) do not alter the implementation's identity in the **Topological Gnosis-Graph (TGG)**.

## Core Axioms
1.  **Functional Parity**: If two source files produce the same AST (after normalization), they share the same UCH.
2.  **Techne-Rigidity**: The hash must be resilient to "dross" (comments, documentation, metadata).
3.  **Cross-Language Uniformity**: The interface for generating and verifying hashes should be consistent across supported languages.

---

## Language Implementations

### 1. Python (ZLV-Alpha)
-   **Parser**: `ast` (Standard Library)
-   **Normalization**:
    -   Strip all `Docstrings`.
    -   Strip all `Type Hints` (annotations).
    -   Strip `Comments` (intrinsic to AST parsing).
    -   Standardize `AnnAssign` to `Assign`.
-   **Hashing**: SHA-256 of the `ast.dump(tree, annotate_fields=False, include_attributes=False)` output.

### 2. TypeScript (UCH-Beta)
-   **Parser**: `tree-sitter-typescript` or `typescript-eslint` parser.
-   **Normalization**:
    -   Remove `Comments` (leading/trailing/interstitial).
    -   Remove `Type Annotations` (interfaces, types, `: type`, `as type`).
    -   Strip `Export` modifiers if only functional logic is being checked.
    -   Normalize `Import` ordering.
-   **Hashing**: SHA-256 of the serialized JSON-AST or a canonical string representation of the tree.

### 3. Shell Scripts (UCH-Gamma)
-   **Parser**: `bashlex` or `tree-sitter-bash`.
-   **Normalization**:
    -   Strip all `#` comments.
    -   Normalize whitespace (tabs/multiple spaces to single space).
    -   Ignore `set -x` or other debugging flags if not core to logic.
-   **Hashing**: SHA-256 of the normalized command stream.

---

## Interface Specification

### `generate_uch(source: string, lang: string) -> string`
Returns the 64-character hex SHA-256 hash.

### `verify_uch(source: string, expected_hash: string, lang: string) -> boolean`
Compares the actual UCH of the source against an expected value.

---

## Integration with RDS Triad
-   **Athena (Logic)**: Validates UCH during the **Refractive Correction** loop in `xnai-gnosis`.
-   **Lilith (Security)**: Uses UCH to ensure that security gates (`Phylax`) haven't been tampered with by adding non-functional noise.
-   **Isis (Integration)**: Maps UCH signatures between service meshes to ensure API contract parity.

## Implementation Roadmap
1.  [x] Python ZLV Rigidity (v1.0)
2.  [ ] TypeScript UCH-Beta Prototype (v1.1)
3.  [ ] Shell UCH-Gamma Basic Parser (v1.2)
4.  [ ] Universal ALETHIA_REGISTRY integration (v2.0)
