# Crawl4AI Advanced Ingestion (XNAi Foundation)

**Status**: 🟢 CURRENT  
**Last Updated**: 2026-02-28  
**Owner**: MC-Overseer  
**Domain**: Infrastructure

---

## Overview

In the XNAi Foundation stack, **Crawl4AI** (v1.0+) is the primary engine for high-signal data ingestion. It is optimized for extracting "AI-Ready" Markdown while managing complex browser states, persistent sessions, and anti-detection mechanisms on the Ryzen 5700U host.

---

## 🚀 Advanced Markdown Extraction

Crawl4AI goes beyond simple HTML-to-MD conversion by employing a multi-stage cleaning pipeline:

### 1. Fit Markdown (Flagship)
- **Mechanism**: Uses **BM25** and **Pruning** algorithms to identify the "core" content.
- **Impact**: Automatically strips headers, footers, sidebars, and ads, delivering only the high-value text.
- **Config**: Set `content_source: "fit_html"` in `markdown_generator_config`.

### 2. Element Targeting
- **CSS Selectors**: Focus extraction on specific relevant areas (e.g., `main-content`, `article-body`).
- **Pruning**: Remove known noise elements (e.g., `.nav`, `#footer`) before conversion.

---

## 🛠 Browser Context & Session Persistence

Crawl4AI utilizes **Managed Browsers** via Playwright to handle authenticated and stateful workflows:

### 1. Persistent Identities
- **User Data Dir**: Specify a host directory (e.g., `./.cache/crawl4ai/profiles`) to store cookies, cache, and session tokens.
- **Identity CLI**: Use `crwl profiles` to manually log in to sites once; Crawl4AI then reuses this state for subsequent headless crawls.

### 2. Sequential Sessions (`session_id`)
Reuse the same browser tab across multiple `arun()` calls:
- **Use Case**: Navigate/Login on Page A → Extract on Page B → Paginate to Page C.
- **Benefit**: Maintains session state without expensive re-logins or re-initialization.

### 3. Magic Mode (Stealth)
A high-level toggle that combines:
- **Fingerprint Randomization**: Bypasses bot detection.
- **Human-like Interaction**: Randomized delays and scrolling.
- **Wait-for-Load Logic**: Ensures dynamic SPA content is fully rendered.

---

## 📈 Operational Workflows

### 1. Multi-Step Ingestion
For documentation behind login walls or with complex navigation:
1. Initialize `AsyncWebCrawler` with a persistent `BrowserConfig`.
2. Step 1: `arun()` to login or navigate.
3. Step 2: `arun()` with `session_id` to extract content.

### 2. High-Throughput Batching
Crawl4AI supports asynchronous batching. In the XNAi stack, this is managed by the `crawler_job_processor.py`, which distributes tasks across multiple workers while respecting rate limits.

### 3. Health Checks
```bash
python3 -c "from crawl4ai import AsyncWebCrawler; import asyncio; asyncio.run(AsyncWebCrawler().start())"
```

---

## ⚠️ Known Issues & Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Empty Markdown | SPA content not rendered | Enable `Magic Mode` or use `wait_until: "networkidle"`. |
| Blocked by WAF | Detected as bot | Enable `Stealth Mode` and use a persistent user-agent. |
| Memory Pressure | Too many browser contexts | Limit concurrent tasks or use a shared `session_id`. |

---

## 📚 References
- [Crawl4AI Official Docs](https://docs.crawl4ai.com/)
- [XNAi Crawler Job Processor](scripts/crawler_job_processor.py)
