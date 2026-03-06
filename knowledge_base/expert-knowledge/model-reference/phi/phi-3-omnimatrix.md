Model card: Phi-3-Omnimatrix (research candidate)
Path: Hugging Face (microsoft Phi family pages) e.g., https://huggingface.co/microsoft/phi-4-gguf and related

Summary
- "Phi-3-Omnimatrix" is treated as an umbrella label for Phi-3 family candidate(s) to evaluate for local inference.
- HF search shows Microsoft Phi family variants (phi-2, phi-3-mini, phi-3.5, phi-4, GGUF builds).

Use-cases
- Deterministic instruction-following for medium-length synthesis when Gemma ONNX not ideal; candidate for local GGUF or ONNX conversion.

Knowledge gaps / Research tasks
- Determine which Phi-3 variant fits memory budget (Phi-3-mini / Phi-3.5-mini-instruct are promising)
- Acquire GGUF artifacts and test with llama.cpp or onnxruntime (for onnx variants)
- Verify license and allowed usages for offline deployment

Next steps
- Prioritize microsoft/Phi-3-mini-4k-instruct and microsoft/phi-4-gguf for smoke tests
- Create Vikunja task to fetch HF model cards and run local perf tests (conversion + inference)
