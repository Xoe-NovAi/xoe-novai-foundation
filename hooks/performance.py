"""
MkDocs Build Performance Monitoring Hook
Tracks build times and generates performance reports for optimization

Research Source: MkDocs hooks documentation, enterprise build monitoring practices
Implementation: Comprehensive performance tracking for 569+ file documentation builds
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime

log = logging.getLogger('mkdocs.plugins.performance')

class BuildMetrics:
    """Tracks comprehensive build performance metrics"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.phase_times = {}
        self.file_count = 0
        self.build_config = {}

    def to_dict(self):
        """Convert metrics to dictionary for JSON serialization"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_duration': self.end_time - self.start_time if self.end_time else None,
            'phases': self.phase_times,
            'file_count': self.file_count,
            'build_config': self.build_config,
            'performance_targets': {
                'target_build_time': '< 60 seconds',
                'current_status': 'WARNING' if (self.end_time - self.start_time) > 120 else 'GOOD'
            }
        }

# Global metrics instance
metrics = BuildMetrics()

def on_startup(command, **kwargs):
    """
    Called when MkDocs starts - initialize performance tracking

    Args:
        command: MkDocs command being executed ('build', 'serve', etc.)
    """
    metrics.start_time = time.time()
    metrics.build_config['command'] = command
    metrics.build_config['start_time'] = datetime.now().isoformat()

    log.info(f"📊 Build performance monitoring started for command: {command}")

def on_pre_build(config, **kwargs):
    """
    Before build starts - record pre-build phase start

    Args:
        config: MkDocs configuration object
    """
    phase_start = time.time()
    metrics.phase_times['pre_build'] = phase_start
    metrics.build_config['strict_mode'] = config.get('strict', False)
    metrics.build_config['theme'] = config.get('theme', {}).get('name', 'unknown')

    log.info("🔧 Pre-build phase started")

def on_files(files, config, **kwargs):
    """
    After files are collected - track file processing performance

    Args:
        files: List of file objects
        config: MkDocs configuration object
    """
    if 'pre_build' in metrics.phase_times:
        duration = time.time() - metrics.phase_times['pre_build']
        metrics.phase_times['files_collection'] = duration
        metrics.file_count = len(files)

        log.info(f"⏱️  Files collected in {duration:.2f}s ({len(files)} files)")

        # Performance warnings for large documentation sets
        if len(files) > 500:
            log.warning(f"⚠️  Large documentation set detected: {len(files)} files")
            if duration > 10:
                log.warning("⚠️  File collection took >10s - consider optimization")

    return files

def on_post_build(config, **kwargs):
    """
    After build completes - record final metrics and generate report

    Args:
        config: MkDocs configuration object
    """
    metrics.end_time = time.time()
    total_duration = metrics.end_time - metrics.start_time

    # Log comprehensive performance summary
    log.info(f"✅ Build completed in {total_duration:.2f}s")

    # Performance analysis and warnings
    if total_duration > 120:
        log.warning(f"⚠️  Build took {total_duration:.2f}s (target: <60s)")
        log.warning("   Consider enabling build cache plugin or optimizing plugins")
    elif total_duration > 60:
        log.info(f"ℹ️  Build took {total_duration:.2f}s (acceptable for large docs)")
    else:
        log.info(f"🚀 Excellent build performance: {total_duration:.2f}s")

    # Save detailed metrics to file
    metrics_file = Path('.cache/mkdocs/performance.json')
    metrics_file.parent.mkdir(parents=True, exist_ok=True)

    with open(metrics_file, 'w') as f:
        json.dump(metrics.to_dict(), f, indent=2)

    log.info(f"📈 Performance metrics saved to {metrics_file}")

    # Log recommendations based on performance
    if total_duration > 90:
        log.info("💡 Performance Recommendations:")
        if not config.get('plugins', {}).get('build_cache'):
            log.info("   - Enable mkdocs-build-cache-plugin for 80% faster incremental builds")
        if not any(p.get('minify') for p in config.get('plugins', [])):
            log.info("   - Enable minify plugin for 40-60% smaller production builds")
        log.info("   - Consider disabling unused plugins in development")

def on_page_markdown(markdown, page, config, files, **kwargs):
    """
    Track page processing performance (optional - can be resource intensive)

    Note: This hook can be expensive for large sites, so it's commented out by default.
    Uncomment if detailed per-page performance analysis is needed.
    """
    # Uncomment for detailed page-level performance tracking
    # page_start = time.time()
    # yield markdown
    # page_duration = time.time() - page_start
    # if page_duration > 1.0:  # Log slow pages
    #     log.warning(f"🐌 Slow page processing: {page.file.src_path} ({page_duration:.2f}s)")
    # return markdown

    return markdown

def on_page_content(html, page, config, files, **kwargs):
    """
    Track page content processing (optional)

    Note: Similar to on_page_markdown, commented out by default.
    """
    return html
