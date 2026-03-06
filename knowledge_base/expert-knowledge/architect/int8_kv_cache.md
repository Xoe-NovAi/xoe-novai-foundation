# Xoe-NovAi Expert Knowledge: Int8 KV Cache Optimization

## Overview
As of v0.1.5, Xoe-NovAi supports Int8 quantization for the LLM Key-Value (KV) cache. This optimization significantly reduces memory usage for long-context interactions, typically halving the RAM required for the cache portion of the model.

## Implementation Details
The optimization is implemented in `app/XNAi_rag_app/dependencies.py` and utilizes the `type_k` and `type_v` parameters of `llama-cpp-python`.

### Parameters
- **F16 (Default)**: `type_k=1, type_v=1`. High precision, standard memory usage.
- **Int8 (Q8_0)**: `type_k=8, type_v=8`. 8-bit quantization, ~50% memory savings for the cache.

### Configuration
Enable Int8 KV cache by setting the following environment variable:
```bash
LLAMA_CPP_CACHE_TYPE=q8_0
# or
LLAMA_CPP_CACHE_TYPE=int8
```

## Performance Impact
- **Memory**: For a 4096 context window, Int8 KV cache can save ~512MB to 1GB of RAM depending on the model architecture.
- **Latency**: Negligible impact on inference speed on Ryzen 5700U; in some cases, slightly faster due to reduced memory bandwidth pressure.
- **Accuracy**: Minimal impact (<1% perplexity increase) for most RAG and conversation tasks.

## Dynamic Precision Consideration
While `llama-cpp-python` requires the cache type to be set at initialization, "dynamic" switching can be achieved by:
1. Restarting the service with a different `LLAMA_CPP_CACHE_TYPE`.
2. Implementing a model-reload trigger (heavy operation).

Currently, Xoe-NovAi prioritizes stability and uses the environment variable approach.

## Verification
Monitor logs for:
`"Enabling Int8 (Q8_0) KV cache for memory savings"`
This confirms the setting is active during LLM initialization.
