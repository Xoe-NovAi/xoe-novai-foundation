---
title: Release V0.7.1
service: crawl4ai
source_urls: ["/tmp/tmp8gy_t8zd/repo/docs/blog/release-v0.7.1.md"]
scraped_at: 2026-02-17T00:26:49.740530
content_hash: c4fd92c1dc11c36a9d3ca6bf429665eb61c41a9a4155d63cd61d8de994acdffb
size_kb: 1.17
---

# 🛠️ Crawl4AI v0.7.1: Minor Cleanup Update

*July 17, 2025 • 2 min read*

---

A small maintenance release that removes unused code and improves documentation.

## 🎯 What's Changed

- **Removed unused StealthConfig** from `crawl4ai/browser_manager.py`
- **Updated documentation** with better examples and parameter explanations
- **Fixed virtual scroll configuration** examples in docs

## 🧹 Code Cleanup

Removed unused `StealthConfig` import and configuration that wasn't being used anywhere in the codebase. The project uses its own custom stealth implementation through JavaScript injection instead.

```python
# Removed unused code:
from playwright_stealth import StealthConfig
stealth_config = StealthConfig(...)  # This was never used
```

## 📖 Documentation Updates

- Fixed adaptive crawling parameter examples
- Updated session management documentation
- Corrected virtual scroll configuration examples

## 🚀 Installation

```bash
pip install crawl4ai==0.7.1
```

No breaking changes - upgrade directly from v0.7.0.

---

Questions? Issues? 
- GitHub: [github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)
- Discord: [discord.gg/crawl4ai](https://discord.gg/jP8KfhDhyN)