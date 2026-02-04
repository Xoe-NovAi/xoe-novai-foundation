# EKB Gem: crawl4ai v0.7.x Async Migration & Standby Mode
**Category:** Coder / Python
**Date**: 2026-01-26
**Issue**: `crawl4ai` v0.7.x removed or relocated the legacy synchronous `WebCrawler` class, causing `ImportError` and runtime failures in existing crawler scripts.

## Root Cause
- **API Shift**: The library moved from synchronous `WebCrawler` to `AsyncWebCrawler` as the primary interface in v0.7.0+.
- **Legacy Module**: Synchronous support was moved to `crawl4ai.legacy.web_crawler`, but this module is incomplete or lacks necessary sub-dependencies (e.g., `models`), making it unreliable for production.

## Remediation: The Async Pivot
The most robust solution is a full migration to the async API:
1. **Import**: `from crawl4ai import AsyncWebCrawler, BrowserConfig`.
2. **Hardware Optimization**: Initialize with stable container-aware flags:
   ```python
   config = BrowserConfig(
       browser_type="chromium",
       headless=True,
       extra_args=[
           "--disable-dev-shm-usage", 
           "--no-sandbox", 
           "--single-process", # Ryzen optimization for lower RAM usage
           "--disable-gpu"
       ]
   )
   crawler = AsyncWebCrawler(config=config)
   ```
3. **Lifecycle**: Use a `try...finally` block to ensure `await crawler.close()` is called, preventing zombie browser processes.
4. **Execution**: Replace `crawler.run(url=...)` with `await crawler.arun(url=...)`.
5. **Non-Blocking I/O**: Wrap legacy blocking calls like `yt-dlp` in `asyncio.to_thread` to prevent freezing the event loop.

## Enterprise Pattern: Standby Service Mode
In containerized environments (Docker/Podman), running a one-shot CLI script as the `CMD` causes the container to exit immediately. For an "Ingestion Engine" service:
1. **Standby CMD**: Use `["sh", "-c", "echo '🚀 Crawler standby...' && while true; do sleep 3600; done"]`.
2. **Ad-hoc Execution**: Run specific curation tasks via `podman exec -it xnai_crawler python3 XNAi_rag_app/crawl.py --curate <source>`.
3. **Persistence**: Use the `:Z,U` volume flag suffix in `docker-compose.yml` to ensure all volumes (`/library`, `/knowledge`, `/app/.crawl4ai`) are mounted with correct automatic ownership mapping.

## Prevention
- **API Monitoring**: Track breaking changes in high-velocity libraries like `crawl4ai`.
- **Async-First**: Default to async implementations for I/O bound services (crawlers, APIs) to avoid legacy technical debt.
- **Standby Strategy**: Design utility services to remain alive in the stack rather than exiting after initial setup.