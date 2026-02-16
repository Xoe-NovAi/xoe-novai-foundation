Model card: functiongemma-270m-it-Q6_K.gguf
Path: models/functiongemma-270m-it-Q6_K.gguf
Format: GGUF (quantized)
Primary role: Lightweight function assistant for prompt transformation, small validators, and tooling glue.
Recommended runtimes: llama.cpp / ggml.
Primary use-cases: small token transformations, prompt sanitization, quick validators used as a second pass.
Knowledge gaps / research tasks:
- Confirm exact quantization layout and its impact on few-shot behavior.
- Build small utility wrappers for common operations (truncate, clean, JSON-verify).
Next steps:
- Add functiongemma to the verification pipeline as the fast, low-cost second pass.