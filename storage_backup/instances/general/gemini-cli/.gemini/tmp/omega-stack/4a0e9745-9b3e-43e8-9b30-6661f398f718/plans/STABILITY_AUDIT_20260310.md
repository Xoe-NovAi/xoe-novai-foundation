# 🏥 Stability Audit: Gemini CLI & Metropolis Foundation (2026-03-10)

## 🚨 Incident: Node.js Heap Out of Memory (OOM)
- **Timestamp**: 2026-03-10 16:30 (approx)
- **Trigger**: `podman logs xnai_llama_server` produced a massive repetitive log (millions of characters) due to a crash loop.
- **Error**: `FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory`.
- **Impact**: Gemini CLI crashed, requiring restart. Context instability reached.

## 🛠️ Service Failure: xnai_llama_server
- **Error**: `FileNotFoundError: Shared library with base name 'llama' not found`.
- **Details**: The `llama-cpp-python` library within the container could not find its backend shared library (`libllama.so` or similar).
- **Likely Cause**: Incompatible container image layers or missing build-time dependencies in `ghcr.io/abetlen/llama-cpp-python:latest`.

## 📈 Resource Usage Analysis (Pending)
- **Reported**: ~20% constant CPU usage by Gemini CLI.
- **Impact**: UI lag and reduced responsiveness.
- **Hypothesis**: Processing a large context window (>80% used) or an active file watcher process.

## 📋 Remediation Tasks
1. [ ] Implement **Local Model Chat Trimming Protocol** (SESS-15).
2. [ ] Fix `xnai_llama_server` image/shared library linkage.
3. [ ] Profile Gemini CLI background processes (Watcher vs. Context Processing).
4. [ ] Implement tool-level output truncation to prevent future OOMs.
