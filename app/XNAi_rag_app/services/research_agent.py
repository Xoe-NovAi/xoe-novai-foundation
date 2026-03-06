#!/usr/bin/env python3
"""
Xoe-NovAi Research and Best Practice Agent
==========================================

Background agent that monitors research, documentation, and code quality.
Automatically suggests improvements, updates best practices, and ensures
the stack remains current with AI/ML advancements.

Features:
- Research monitoring and updates
- Documentation freshness validation
- Code quality and best practice enforcement
- AI/ML advancement tracking
- Automated improvement suggestions

Author: Xoe-NovAi Development Team
Date: January 17, 2026
"""

import os
import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import threading
import hashlib
import re

# Import metrics for monitoring
try:
    from XNAi_rag_app.core.metrics import record_structured_log_event, update_knowledge_freshness
except ImportError:
    # Fallback for testing
    def record_structured_log_event(*args): pass
    def update_knowledge_freshness(*args): pass

logger = logging.getLogger(__name__)

class ResearchBestPracticeAgent:
    """
    Background agent for research monitoring and best practice enforcement.

    Monitors:
    - Research document freshness and relevance
    - Documentation completeness and accuracy
    - Code quality and architectural patterns
    - AI/ML advancement integration
    - Security and performance best practices
    """

    def __init__(
        self,
        project_root: Optional[str] = None,
        check_interval_hours: int = 24,
        enable_auto_updates: bool = False
    ):
        self.project_root = Path(project_root or Path(__file__).parent.parent.parent)
        self.check_interval = timedelta(hours=check_interval_hours)
        self.enable_auto_updates = enable_auto_updates

        # Monitoring state
        self.last_check = datetime.min
        self.monitoring_active = False
        self.monitor_thread = None

        # Research and documentation tracking
        self.research_docs: Dict[str, Dict[str, Any]] = {}
        self.documentation_files: Dict[str, Dict[str, Any]] = {}
        self.code_quality_issues: List[Dict[str, Any]] = []

        # AI/ML advancement tracking
        self.tracked_technologies = {
            'quantization': {'awq', 'gptq', 'gguf'},
            'acceleration': {'vulkan', 'cuda', 'rocm'},
            'models': {'transformers', 'llm', 'embedding'},
            'optimization': {'pruning', 'distillation', 'quantization'}
        }

        # Best practice rules
        self.best_practice_rules = self._load_best_practice_rules()

        # Initialize monitoring
        self._initialize_tracking()

    def _load_best_practice_rules(self) -> Dict[str, Any]:
        """Load best practice validation rules."""
        return {
            'documentation': {
                'freshness_days': 30,
                'required_sections': ['overview', 'installation', 'usage', 'api'],
                'code_examples': True,
                'troubleshooting': True
            },
            'code_quality': {
                'max_complexity': 10,
                'min_test_coverage': 80,
                'required_logging': True,
                'error_handling': True,
                'type_hints': True
            },
            'security': {
                'input_validation': True,
                'secrets_management': True,
                'dependency_scanning': True,
                'access_controls': True
            },
            'performance': {
                'memory_limits': True,
                'timeout_handling': True,
                'resource_monitoring': True,
                'optimization_opportunities': True
            }
        }

    def _initialize_tracking(self):
        """Initialize file and research tracking."""
        # Track research documents
        research_paths = [
            self.project_root / 'docs' / 'ai-research',
            self.project_root / 'docs' / 'deep_research',
            self.project_root / 'docs' / 'research'
        ]

        for research_path in research_paths:
            if research_path.exists():
                for md_file in research_path.glob('**/*.md'):
                    self._track_research_document(md_file)

        # Track documentation files
        docs_path = self.project_root / 'docs'
        if docs_path.exists():
            for md_file in docs_path.glob('**/*.md'):
                self._track_documentation_file(md_file)

        logger.info(f"Initialized tracking: {len(self.research_docs)} research docs, {len(self.documentation_files)} docs")

    def _track_research_document(self, file_path: Path):
        """Track a research document for freshness monitoring."""
        try:
            stat = file_path.stat()
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata
            metadata = self._extract_document_metadata(content)

            self.research_docs[str(file_path)] = {
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'content_hash': hashlib.md5(content.encode()).hexdigest(),
                'metadata': metadata,
                'last_reviewed': datetime.now(),
                'freshness_score': self._calculate_freshness_score(metadata)
            }

        except Exception as e:
            logger.warning(f"Failed to track research document {file_path}: {e}")

    def _track_documentation_file(self, file_path: Path):
        """Track a documentation file for completeness monitoring."""
        try:
            stat = file_path.stat()
            content = file_path.read_text(encoding='utf-8')

            # Analyze documentation quality
            quality_metrics = self._analyze_documentation_quality(content)

            self.documentation_files[str(file_path)] = {
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'content_hash': hashlib.md5(content.encode()).hexdigest(),
                'quality_metrics': quality_metrics,
                'last_reviewed': datetime.now(),
                'completeness_score': quality_metrics.get('completeness_score', 0)
            }

        except Exception as e:
            logger.warning(f"Failed to track documentation file {file_path}: {e}")

    def _extract_document_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from document content."""
        metadata = {
            'title': '',
            'date': None,
            'author': '',
            'tags': [],
            'technologies': [],
            'references': [],
            'outdated_indicators': []
        }

        # Extract frontmatter
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end != -1:
                frontmatter = content[3:frontmatter_end]
                # Parse YAML-like frontmatter (simplified)
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"').strip("'")

                        if key == 'title':
                            metadata['title'] = value
                        elif key == 'date':
                            try:
                                metadata['date'] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            except:
                                pass
                        elif key == 'author':
                            metadata['author'] = value
                        elif key == 'tags':
                            metadata['tags'] = [tag.strip() for tag in value.split(',')]

        # Extract technology mentions
        tech_patterns = {
            'awq': r'\bAWQ\b',
            'gptq': r'\bGPTQ\b',
            'vulkan': r'\bVulkan\b',
            'cuda': r'\bCUDA\b',
            'transformers': r'\btransformers?\b',
            'quantization': r'\bquantization\b'
        }

        for tech, pattern in tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                metadata['technologies'].append(tech)

        # Check for outdated indicators
        outdated_patterns = [
            r'\bdeprecated\b',
            r'\boutdated\b',
            r'\bolegacy\b',
            r'\bno longer supported\b',
            r'\breplaced by\b'
        ]

        for pattern in outdated_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                metadata['outdated_indicators'].append(pattern)

        return metadata

    def _analyze_documentation_quality(self, content: str) -> Dict[str, Any]:
        """Analyze documentation quality metrics."""
        metrics = {
            'completeness_score': 0,
            'has_overview': False,
            'has_installation': False,
            'has_usage': False,
            'has_api_docs': False,
            'has_examples': False,
            'has_troubleshooting': False,
            'code_blocks': 0,
            'links': 0,
            'readability_score': 0
        }

        # Check for required sections
        content_lower = content.lower()
        metrics['has_overview'] = any(word in content_lower for word in ['overview', 'introduction', 'summary'])
        metrics['has_installation'] = any(word in content_lower for word in ['install', 'setup', 'getting started'])
        metrics['has_usage'] = any(word in content_lower for word in ['usage', 'how to', 'guide'])
        metrics['has_api_docs'] = any(word in content_lower for word in ['api', 'reference', 'function'])
        metrics['has_examples'] = '```' in content or 'code' in content_lower
        metrics['has_troubleshooting'] = any(word in content_lower for word in ['troubleshoot', 'error', 'issue'])

        # Count code blocks and links
        metrics['code_blocks'] = content.count('```')
        metrics['links'] = content.count('](')

        # Calculate completeness score
        section_score = sum([
            metrics['has_overview'],
            metrics['has_installation'],
            metrics['has_usage'],
            metrics['has_api_docs'],
            metrics['has_examples'],
            metrics['has_troubleshooting']
        ]) / 6

        quality_score = min(1.0, (metrics['code_blocks'] / 10) + (metrics['links'] / 20))
        metrics['completeness_score'] = (section_score + quality_score) / 2

        return metrics

    def _calculate_freshness_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate research document freshness score."""
        now = datetime.now()
        score = 1.0

        # Date-based freshness
        if metadata.get('date'):
            days_old = (now - metadata['date']).days
            if days_old > 365:
                score *= 0.3
            elif days_old > 180:
                score *= 0.6
            elif days_old > 90:
                score *= 0.8

        # Technology relevance
        current_techs = {'awq', 'vulkan', 'quantization', 'transformers'}
        mentioned_techs = set(metadata.get('technologies', []))
        tech_overlap = len(current_techs & mentioned_techs) / len(current_techs)
        score *= (0.5 + 0.5 * tech_overlap)

        # Outdated indicators reduce score
        outdated_count = len(metadata.get('outdated_indicators', []))
        score *= max(0.1, 1.0 - (outdated_count * 0.2))

        return score

    async def run_monitoring_cycle(self):
        """Run a complete monitoring cycle."""
        logger.info("Starting research and best practice monitoring cycle")

        # Check research freshness
        await self._check_research_freshness()

        # Validate documentation quality
        await self._validate_documentation_quality()

        # Scan for code quality issues
        await self._scan_code_quality()

        # Check for AI/ML advancements
        await self._check_ai_advancements()

        # Generate improvement suggestions
        suggestions = await self._generate_improvement_suggestions()

        # Auto-apply improvements if enabled
        if self.enable_auto_updates and suggestions:
            await self._apply_auto_updates(suggestions)

        # Update metrics
        self._update_monitoring_metrics()

        logger.info("Completed research and best practice monitoring cycle")

    async def _check_research_freshness(self):
        """Check freshness of research documents."""
        logger.info("Checking research document freshness")

        stale_docs = []
        for doc_path, doc_info in self.research_docs.items():
            days_old = (datetime.now() - doc_info['modified']).days
            freshness_score = doc_info['freshness_score']

            # Flag documents that need attention
            if days_old > 90 or freshness_score < 0.6:
                stale_docs.append({
                    'path': doc_path,
                    'days_old': days_old,
                    'freshness_score': freshness_score,
                    'recommendation': 'Review and update research findings'
                })

        if stale_docs:
            logger.warning(f"Found {len(stale_docs)} stale research documents")
            for doc in stale_docs:
                record_structured_log_event(
                    'WARNING',
                    'research_agent',
                    'stale_research',
                    'medium'
                )

    async def _validate_documentation_quality(self):
        """Validate documentation completeness and quality."""
        logger.info("Validating documentation quality")

        poor_quality_docs = []
        for doc_path, doc_info in self.documentation_files.items():
            completeness_score = doc_info['completeness_score']
            quality_metrics = doc_info['quality_metrics']

            if completeness_score < 0.7:
                poor_quality_docs.append({
                    'path': doc_path,
                    'completeness_score': completeness_score,
                    'missing_sections': self._identify_missing_sections(quality_metrics),
                    'recommendation': 'Improve documentation completeness'
                })

        if poor_quality_docs:
            logger.warning(f"Found {len(poor_quality_docs)} poor quality documentation files")
            for doc in poor_quality_docs:
                record_structured_log_event(
                    'WARNING',
                    'research_agent',
                    'poor_documentation',
                    'low'
                )

    def _identify_missing_sections(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Identify missing documentation sections."""
        missing = []
        if not quality_metrics.get('has_overview'):
            missing.append('overview')
        if not quality_metrics.get('has_installation'):
            missing.append('installation')
        if not quality_metrics.get('has_usage'):
            missing.append('usage')
        if not quality_metrics.get('has_api_docs'):
            missing.append('API documentation')
        if not quality_metrics.get('has_examples'):
            missing.append('code examples')
        if not quality_metrics.get('has_troubleshooting'):
            missing.append('troubleshooting')
        return missing

    async def _scan_code_quality(self):
        """Scan codebase for quality issues."""
        logger.info("Scanning code quality")

        # This would integrate with tools like pylint, black, mypy
        # For now, do basic checks
        code_issues = []

        python_files = list(self.project_root.glob('**/*.py'))
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')

                # Check for basic quality issues
                issues = self._analyze_code_quality(content, str(py_file))
                if issues:
                    code_issues.extend(issues)

            except Exception as e:
                logger.warning(f"Failed to analyze {py_file}: {e}")

        self.code_quality_issues = code_issues

        if code_issues:
            logger.warning(f"Found {len(code_issues)} code quality issues")
            for issue in code_issues:
                record_structured_log_event(
                    'INFO',
                    'research_agent',
                    'code_quality_issue',
                    'low'
                )

    def _analyze_code_quality(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze code quality for a single file."""
        issues = []

        # Check for missing type hints (basic)
        if 'def ' in content and '->' not in content:
            issues.append({
                'file': file_path,
                'type': 'missing_type_hints',
                'severity': 'low',
                'description': 'Consider adding type hints to function definitions'
            })

        # Check for bare except clauses
        if 'except:' in content:
            issues.append({
                'file': file_path,
                'type': 'bare_except',
                'severity': 'medium',
                'description': 'Avoid bare except clauses; specify exception types'
            })

        # Check for TODO comments
        todo_count = content.upper().count('TODO')
        if todo_count > 0:
            issues.append({
                'file': file_path,
                'type': 'todo_comments',
                'severity': 'low',
                'description': f'Found {todo_count} TODO comment(s) to address'
            })

        return issues

    async def _check_ai_advancements(self):
        """Check for AI/ML advancements that could improve the stack."""
        logger.info("Checking for AI/ML advancements")

        # This would typically query APIs or check for updates
        # For now, provide basic recommendations
        advancements = [
            {
                'technology': 'AWQ',
                'status': 'implemented',
                'recommendation': 'Monitor for AWQ v2 developments'
            },
            {
                'technology': 'Vulkan Compute',
                'status': 'implemented',
                'recommendation': 'Consider shader optimization updates'
            },
            {
                'technology': 'Quantization',
                'status': 'active',
                'recommendation': 'Monitor GPTQ and GGUF developments'
            }
        ]

        # Update knowledge base metrics
        for advancement in advancements:
            update_knowledge_freshness(
                advancement['technology'],
                'daily',
                'research',
                1  # days (very fresh)
            )

    async def _generate_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on monitoring."""
        suggestions = []

        # Research update suggestions
        for doc_path, doc_info in self.research_docs.items():
            if doc_info['freshness_score'] < 0.6:
                suggestions.append({
                    'type': 'research_update',
                    'target': doc_path,
                    'priority': 'medium',
                    'description': f'Update research document - freshness score: {doc_info["freshness_score"]:.2f}',
                    'action': 'review_and_update'
                })

        # Documentation improvement suggestions
        for doc_path, doc_info in self.documentation_files.items():
            if doc_info['completeness_score'] < 0.7:
                missing_sections = self._identify_missing_sections(doc_info['quality_metrics'])
                suggestions.append({
                    'type': 'documentation_improvement',
                    'target': doc_path,
                    'priority': 'medium',
                    'description': f'Improve documentation completeness - missing: {", ".join(missing_sections)}',
                    'action': 'add_missing_sections'
                })

        # Code quality suggestions
        for issue in self.code_quality_issues:
            suggestions.append({
                'type': 'code_quality',
                'target': issue['file'],
                'priority': 'low' if issue['severity'] == 'low' else 'medium',
                'description': issue['description'],
                'action': 'fix_code_issue'
            })

        return suggestions

    async def _apply_auto_updates(self, suggestions: List[Dict[str, Any]]):
        """Apply automatic updates for approved suggestions."""
        logger.info(f"Applying {len(suggestions)} auto-updates")

        # For now, just log the suggestions
        # In a full implementation, this would apply safe automated fixes
        for suggestion in suggestions:
            logger.info(f"Auto-update suggestion: {suggestion['description']}")

    def _update_monitoring_metrics(self):
        """Update monitoring metrics."""
        # Update metrics with current state
        record_structured_log_event(
            'INFO',
            'research_agent',
            'monitoring_cycle_complete',
            'low'
        )

    def start_monitoring(self):
        """Start background monitoring."""
        if self.monitoring_active:
            logger.warning("Research agent monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="research-agent-monitor"
        )
        self.monitor_thread.start()

        logger.info("Research and best practice agent monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logger.info("Research and best practice agent monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Check if it's time for a monitoring cycle
                if datetime.now() - self.last_check >= self.check_interval:
                    # Run monitoring cycle (in a new event loop since we're in a thread)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.run_monitoring_cycle())
                    loop.close()

                    self.last_check = datetime.now()

                # Sleep for a shorter interval to check the flag
                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Research agent monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes on error

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            'active': self.monitoring_active,
            'last_check': self.last_check.isoformat() if self.last_check != datetime.min else None,
            'research_docs_tracked': len(self.research_docs),
            'documentation_files_tracked': len(self.documentation_files),
            'code_quality_issues': len(self.code_quality_issues),
            'auto_updates_enabled': self.enable_auto_updates
        }

    def get_research_freshness_report(self) -> Dict[str, Any]:
        """Get research freshness report."""
        docs_by_freshness = {
            'fresh': [],
            'stale': [],
            'outdated': []
        }

        for doc_path, doc_info in self.research_docs.items():
            freshness_score = doc_info['freshness_score']
            if freshness_score >= 0.8:
                docs_by_freshness['fresh'].append(doc_path)
            elif freshness_score >= 0.6:
                docs_by_freshness['stale'].append(doc_path)
            else:
                docs_by_freshness['outdated'].append(doc_path)

        return {
            'total_docs': len(self.research_docs),
            'freshness_distribution': docs_by_freshness,
            'average_freshness_score': sum(doc['freshness_score'] for doc in self.research_docs.values()) / len(self.research_docs) if self.research_docs else 0
        }

# Global agent instance
_research_agent: Optional[ResearchBestPracticeAgent] = None

def get_research_agent() -> ResearchBestPracticeAgent:
    """Get the global research agent instance."""
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchBestPracticeAgent()
    return _research_agent

def start_research_agent(enable_auto_updates: bool = False):
    """Start the research and best practice agent."""
    agent = get_research_agent()
    agent.enable_auto_updates = enable_auto_updates
    agent.start_monitoring()
    logger.info("Research and best practice agent started")

def stop_research_agent():
    """Stop the research and best practice agent."""
    global _research_agent
    if _research_agent:
        _research_agent.stop_monitoring()
        _research_agent = None
        logger.info("Research and best practice agent stopped")

# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Xoe-NovAi Research and Best Practice Agent")
    parser.add_argument("--start", action="store_true", help="Start the monitoring agent")
    parser.add_argument("--stop", action="store_true", help="Stop the monitoring agent")
    parser.add_argument("--status", action="store_true", help="Show agent status")
    parser.add_argument("--auto-updates", action="store_true", help="Enable automatic updates")
    parser.add_argument("--check-now", action="store_true", help="Run immediate monitoring cycle")

    args = parser.parse_args()

    if args.start:
        start_research_agent(enable_auto_updates=args.auto_updates)
        print("Research agent started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_research_agent()

    elif args.stop:
        stop_research_agent()
        print("Research agent stopped.")

    elif args.status:
        agent = get_research_agent()
        status = agent.get_monitoring_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.check_now:
        agent = get_research_agent()
        # Run check in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(agent.run_monitoring_cycle())
        loop.close()
        print("Monitoring cycle completed.")

    else:
        parser.print_help()
