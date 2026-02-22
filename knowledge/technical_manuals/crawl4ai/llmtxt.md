---
title: Llmtxt
service: crawl4ai
source_urls: ["/tmp/tmp8gy_t8zd/repo/docs/md_v2/core/llmtxt.md"]
scraped_at: 2026-02-17T00:26:49.781821
content_hash: 4ccf9c9e925984fa273613ead6696b12b84816430109323672dfe89ccac1db34
size_kb: 1.69
---

I<div class="llmtxt-container">
<iframe id="llmtxt-frame" src="../../llmtxt/index.html" width="100%" style="border:none; display: block;" title="Crawl4AI LLM Context Builder"></iframe>
</div>

<script>
// Iframe height adjustment
function resizeLLMtxtIframe() {
  const iframe = document.getElementById('llmtxt-frame');
  if (iframe) {
    const headerHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-height') || '55');
    const topOffset = headerHeight + 20;
    const availableHeight = window.innerHeight - topOffset;
    iframe.style.height = Math.max(800, availableHeight) + 'px';
  }
}

// Run immediately and on resize/load
resizeLLMtxtIframe();
let resizeTimer;
window.addEventListener('load', resizeLLMtxtIframe);
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resizeLLMtxtIframe, 150);
});

// Remove Footer & HR from parent page
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const footer = window.parent.document.querySelector('footer');
        if (footer) {
            const hrBeforeFooter = footer.previousElementSibling;
            if (hrBeforeFooter && hrBeforeFooter.tagName === 'HR') {
                hrBeforeFooter.remove();
            }
            footer.remove();
            resizeLLMtxtIframe();
        }
    }, 100);
});
</script>

<style>
#terminal-mkdocs-main-content {
    padding: 0 !important;
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

#terminal-mkdocs-main-content .llmtxt-container {
    margin: 0;
    padding: 0;
    max-width: none;
    overflow: hidden;
}

#terminal-mkdocs-toc-panel {
    display: none !important;
}
</style>