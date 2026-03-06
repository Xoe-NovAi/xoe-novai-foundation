---
model_details:
  name: "Model Name"
  version: "1.0.0"
  type: "LLM | Embedding | STT | TTS | Vision"
  architecture: "e.g., Llama-3, Transformer"
  developers: "Original Developer"
  license: "License Type"
  repository: "Link to repo/HuggingFace"
  framework: "e.g., llama.cpp, PyTorch"
  quantization: "e.g., Q4_K_M, AWQ"

xnai_integration:
  status: "Active | Experimental | Planned"
  service: "RAG-API | Voice | Vision-Service"
  hardware_target: "Ryzen CPU | iGPU | Vulkan"
  ram_footprint_mb: 0
  vram_footprint_mb: 0
  latency_ms: 0

intended_use:
  primary: "Primary use case"
  limitations: "What it's bad at"

training_data:
  dataset: "Name of dataset"
  description: "Brief description"

evaluation:
  metrics:
    - name: "Metric Name"
      value: 0.0
---

# Model Name: [Sub-title]

## Overview
Brief overview of the model and why it was chosen for the Xoe-NovAi Foundation.

## Integration Details
How this model is integrated into the XNAi stack (e.g., via `llama-cpp-python`, `whisper.cpp`).

## Performance in Sovereign Environment
Detailed notes on how it performs on Ryzen/iGPU hardware.

## Ethical & Security Considerations
Specific notes on bias, privacy, and zero-telemetry compliance.
