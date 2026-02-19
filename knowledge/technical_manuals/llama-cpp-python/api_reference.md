---
title: Api Reference
service: llama-cpp-python
source_urls: ["/tmp/tmpo5ipr3oa/repo/docs/api-reference.md"]
scraped_at: 2026-02-17T00:26:23.047933
content_hash: 9ef8d0e042ee8456084e8e8f28a5f106a0512a677041623cdf3035a77971856b
size_kb: 1.80
---

---
title: API Reference
---

## High Level API

High-level Python bindings for llama.cpp.

::: llama_cpp.Llama
    options:
        members:
            - __init__
            - tokenize
            - detokenize
            - reset
            - eval
            - sample
            - generate
            - create_embedding
            - embed
            - create_completion
            - __call__
            - create_chat_completion
            - create_chat_completion_openai_v1
            - set_cache
            - save_state
            - load_state
            - token_bos
            - token_eos
            - from_pretrained
        show_root_heading: true

::: llama_cpp.LlamaGrammar
    options:
        members:
            - from_string
            - from_json_schema

::: llama_cpp.LlamaCache
    options:
        show_root_heading: true

::: llama_cpp.LlamaState
    options:
        show_root_heading: true

::: llama_cpp.LogitsProcessor
    options:
        show_root_heading: true

::: llama_cpp.LogitsProcessorList
    options:
        show_root_heading: true

::: llama_cpp.StoppingCriteria
    options:
        show_root_heading: true

::: llama_cpp.StoppingCriteriaList
    options:
        show_root_heading: true

## Low Level API

Low-level Python bindings for llama.cpp using Python's ctypes library.

::: llama_cpp.llama_cpp
    options:
        show_if_no_docstring: true
        # filter only members starting with `llama_`
        filters:
            - "^llama_"

::: llama_cpp.llama_cpp
    options:
        show_if_no_docstring: true
        show_root_heading: false
        show_root_toc_entry: false
        heading_level: 4
        # filter only members starting with `LLAMA_`
        filters:
            - "^LLAMA_"

## Misc

::: llama_cpp.llama_types
    options:
        show_if_no_docstring: true