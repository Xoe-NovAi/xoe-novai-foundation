# Firecrawl Results: llama.cpp Repository

**URL**: https://github.com/ggml-org/llama.cpp  
**Crawled**: January 20, 2026  
**Status**: Success  
**Content Type**: GitHub Repository README  

## Raw Content

[Skip to content](https://github.com/ggml-org/llama.cpp#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ggml-org/llama.cpp) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ggml-org/llama.cpp) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ggml-org/llama.cpp) to refresh your session.Dismiss alert

{{ message }}

[ggml-org](https://github.com/ggml-org)/ **[llama.cpp](https://github.com/ggml-org/llama.cpp)** Public

- [Notifications](https://github.com/login?return_to=%2Fggml-org%2Fllama.cpp)
- [Fork\\\n14.5k](https://github.com/login?return_to=%2Fggml-org%2Fllama.cpp)
- [Star\\\n93.4k](https://github.com/login?return_to=%2Fggml-org%2Fllama.cpp)


LLM inference in C/C++


### License

[MIT license](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE)

[93.4k\\\nstars](https://github.com/ggml-org/llama.cpp/stargazers) [14.5k\\\nforks](https://github.com/ggml-org/llama.cpp/forks) [Branches](https://github.com/ggml-org/llama.cpp/branches) [Tags](https://github.com/ggml-org/llama.cpp/tags) [Activity](https://github.com/ggml-org/llama.cpp/activity)

[Star](https://github.com/login?return_to=%2Fggml-org%2Fllama.cpp)

[Notifications](https://github.com/login?return_to=%2Fggml-org%2Fllama.cpp) You must be signed in to change notification settings

# ggml-org/llama.cpp

master

[**537** Branches](https://github.com/ggml-org/llama.cpp/branches) [**5315** Tags](https://github.com/ggml-org/llama.cpp/tags)

[Go to Branches page](https://github.com/ggml-org/llama.cpp/branches)[Go to Tags page](https://github.com/ggml-org/llama.cpp/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![ORippler](https://avatars.githubusercontent.com/u/24656669?v=4&size=40)](https://github.com/ORippler)[ORippler](https://github.com/ggml-org/llama.cpp/commits?author=ORippler)<br>[CUDA: Fix builds for older CCCL versions by ifdefing strided\\_iterator (](https://github.com/ggml-org/llama.cpp/commit/5bd341c9a135a13f901c4cacacc27fa5b299ce19) […](https://github.com/ggml-org/llama.cpp/pull/18964)<br>Open commit detailspending<br>1 hour agoJan 20, 2026<br>[5bd341c](https://github.com/ggml-org/llama.cpp/commit/5bd341c9a135a13f901c4cacacc27fa5b299ce19) · 1 hour agoJan 20, 2026<br>## History<br>[7,786 Commits](https://github.com/ggml-org/llama.cpp/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/ggml-org/llama.cpp/commits/master/) |

[Repository files truncated for brevity - full content available in raw markdown]

## Architecture Highlights

**Core Capabilities:**
- Plain C/C++ implementation without dependencies
- Apple silicon optimized (ARM NEON, Accelerate, Metal)
- AVX, AVX2, AVX512, AMX support for x86
- 1.5-bit to 8-bit integer quantization
- CUDA, HIP, Vulkan, SYCL backends
- Hybrid CPU+GPU inference

**Supported Models:**
- LLaMA, LLaMA 2/3, Mistral, Mixtral, Grok-1
- BERT, GPT-2, GPT-NeoX, Phi, Qwen
- Multimodal: LLaVA, MiniCPM, Moondream
- 50+ model architectures supported

**Performance Claims:**
- Minimal setup requirements
- State-of-the-art performance on consumer hardware
- Vulkan backend for cross-platform GPU acceleration

**Torch-Free Design:**
- No PyTorch dependencies
- Pure C/C++ inference engine
- GGUF format for quantized models
- Direct hardware optimization

This repository represents the core torch-free inference capability that enables Xoe-NovAi's sovereign AI architecture.
