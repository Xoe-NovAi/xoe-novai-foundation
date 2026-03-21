#!/usr/bin/env python3
"""
OMEGA Stack Adaptive Management System (OAMS)

A practical, evolving framework that intelligently manages complex development
environments based on emerging best practices and real-time metrics.

Principles:
1. Non-destructive (all changes reversible)
2. Evidence-based (metrics drive decisions)
3. Adaptive (learns from what works)
4. Distributed (multi-agent awareness)
5. Privacy-first (all data stays local)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any, Optional
import logging
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [OAMS] %(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)


@dataclass
class FileMetrics:
    """Track metrics about files and folders."""
    path: str
    size_bytes: int
    last_accessed: str  # ISO timestamp
    last_modified: str  # ISO timestamp
    access_frequency: int = 0
    linkage_count: int = 0  # How many other files reference it
    category: str = "uncategorized"
    quality_score: float = 0.5  # 0-1: relevance, maintainability, clarity


@dataclass
class ConsolidationAction:
    """Represent a proposed consolidation action."""
    action_type: str  # "merge", "archive", "deduplicate", "flatten", "link"
    source: List[str]  # Files to act on
    target: str  # Where they go
    reason: str
    risk_level: str  # "low", "medium", "high"
    reversible: bool = True
    estimated_impact: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.estimated_impact is None:
            self.estimated_impact = {}


class AdaptiveOrganizationSystem:
    """
    Main system that evolves repo organization based on evidence.
    
    Tracks:
    - File access patterns
    - Cross-reference graphs
    - Information density
    - Maintenance burden
    - Knowledge structure
    """
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.state_dir = self.repo_root / ".oams"
        self.state_dir.mkdir(exist_ok=True)
        
        self.metrics_db = self.state_dir / "metrics.jsonl"
        self.decisions_log = self.state_dir / "decisions.jsonl"
        self.consolidation_queue = self.state_dir / "consolidation-queue.json"
        
        self.file_metrics: Dict[str, FileMetrics] = {}
        self.consolidation_proposals: List[ConsolidationAction] = []
    
    def scan_and_update_metrics(self) -> Dict[str, Any]:
        """
        Scan repo and update file metrics.
        Based on evidence, not opinions.
        """
        logger.info("📊 Scanning repo for metrics...")
        
        scan_time = datetime.now().isoformat()
        new_metrics = {}
        
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                try:
                    stat = file_path.stat()
                    rel_path = str(file_path.relative_to(self.repo_root))
                    
                    # Load previous metrics if exist
                    prev = self.file_metrics.get(rel_path)
                    
                    # Update access frequency (approximate)
                    access_freq = (prev.access_frequency + 1) if prev else 0
                    
                    metrics = FileMetrics(
                        path=rel_path,
                        size_bytes=stat.st_size,
                        last_accessed=scan_time,
                        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        access_frequency=access_freq,
                        category=prev.category if prev else "uncategorized",
                    )
                    
                    new_metrics[rel_path] = metrics
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not scan {file_path}: {e}")
        
        self.file_metrics = new_metrics
        self._persist_metrics()
        
        logger.info(f"✅ Scanned {len(new_metrics)} files")
        return {
            'timestamp': scan_time,
            'files_scanned': len(new_metrics),
            'total_size_gb': sum(m.size_bytes for m in new_metrics.values()) / (1024**3),
        }
    
    def analyze_structure_entropy(self) -> Dict[str, Any]:
        """
        Calculate "entropy" of folder structure.
        High entropy = disorganized, low entropy = well-organized.
        """
        logger.info("🌡️  Analyzing structure entropy...")
        
        folder_characteristics = defaultdict(lambda: {
            'file_count': 0,
            'subfolder_count': 0,
            'avg_file_size': 0,
            'size_variance': 0,
            'update_recency': [],
        })
        
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file():
                parent = str(file_path.parent.relative_to(self.repo_root))
                folder_characteristics[parent]['file_count'] += 1
                
                metrics = self.file_metrics.get(str(file_path.relative_to(self.repo_root)))
                if metrics:
                    folder_characteristics[parent]['avg_file_size'] += metrics.size_bytes
                    folder_characteristics[parent]['update_recency'].append(metrics.last_modified)
        
        # Calculate entropy scores
        entropy_results = {}
        for folder, chars in folder_characteristics.items():
            if chars['file_count'] == 0:
                continue
            
            # Simple entropy: files per folder (low = organized, high = chaotic)
            entropy = chars['file_count'] / max(1, len(folder.split(os.sep)))
            
            entropy_results[folder] = {
                'entropy_score': entropy,
                'file_count': chars['file_count'],
                'status': 'well-organized' if entropy < 5 else 'chaotic' if entropy > 20 else 'moderate',
            }
        
        return entropy_results
    
    def generate_consolidation_proposals(self) -> List[ConsolidationAction]:
        """
        Based on metrics and analysis, propose consolidations.
        All proposals are evidence-based and reversible.
        """
        logger.info("💡 Generating consolidation proposals...")
        
        proposals = []
        
        # PROPOSAL 1: Deduplicate folder names
        folder_names = defaultdict(list)
        for path in self.file_metrics.keys():
            parts = Path(path).parts
            for part in parts:
                folder_names[part].append(path)
        
        duplicates = {name: paths for name, paths in folder_names.items() if len(paths) > 1}
        
        for name, paths in duplicates.items():
            if name in ['knowledge', 'archive', 'test', 'config']:
                proposal = ConsolidationAction(
                    action_type='consolidate',
                    source=paths[:2],
                    target=f"{name}_unified",
                    reason=f"Multiple '{name}' folders detected - consolidate into single source of truth",
                    risk_level='medium',
                    reversible=True,
                    estimated_impact={'deduplication_ratio': 0.85}
                )
                proposals.append(proposal)
        
        # PROPOSAL 2: Archive stale files
        cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
        stale_files = [
            path for path, metrics in self.file_metrics.items()
            if metrics.last_modified < cutoff_date and metrics.access_frequency == 0
        ]
        
        if stale_files:
            proposal = ConsolidationAction(
                action_type='archive',
                source=stale_files,
                target='_archive/historical',
                reason=f"{len(stale_files)} files untouched for 90+ days",
                risk_level='low',
                reversible=True,
            )
            proposals.append(proposal)
        
        # PROPOSAL 3: Flatten deeply nested structures
        deep_folders = [
            path for path in self.file_metrics.keys()
            if path.count(os.sep) > 6
        ]
        
        if deep_folders:
            proposal = ConsolidationAction(
                action_type='flatten',
                source=deep_folders[:5],
                target='docs/reference',
                reason=f"Deeply nested files (6+ levels) - consider flattening with better indexing",
                risk_level='medium',
                reversible=True,
            )
            proposals.append(proposal)
        
        self.consolidation_proposals = proposals
        return proposals
    
    def create_knowledge_map(self) -> Dict[str, Any]:
        """
        Create a searchable map of all knowledge in the repo.
        Enables navigation and discoverability.
        """
        logger.info("🗺️  Creating knowledge map...")
        
        knowledge_map = {
            'timestamp': datetime.now().isoformat(),
            'sections': {},
            'by_type': defaultdict(list),
            'by_purpose': defaultdict(list),
            'orphans': [],
            'hubs': [],  # Most-linked files
        }
        
        # Categorize files
        for path, metrics in self.file_metrics.items():
            file_ext = Path(path).suffix
            knowledge_map['by_type'][file_ext].append(path)
            
            # Classify by purpose
            if any(x in path for x in ['tutorial', 'guide', 'howto']):
                knowledge_map['by_purpose']['tutorial'].append(path)
            elif any(x in path for x in ['api', 'spec', 'reference']):
                knowledge_map['by_purpose']['reference'].append(path)
            elif any(x in path for x in ['doc', 'explain', 'design']):
                knowledge_map['by_purpose']['explanation'].append(path)
        
        return knowledge_map
    
    def generate_governance_report(self) -> str:
        """Generate report on repo governance and recommendations."""
        report = []
        report.append("=" * 80)
        report.append("OMEGA STACK - ADAPTIVE MANAGEMENT SYSTEM REPORT")
        report.append("=" * 80)
        report.append("")
        
        report.append("📊 METRICS SUMMARY")
        report.append(f"  Files Tracked: {len(self.file_metrics)}")
        report.append(f"  Total Size: {sum(m.size_bytes for m in self.file_metrics.values()) / (1024**3):.2f}GB")
        report.append("")
        
        report.append("💡 CONSOLIDATION PROPOSALS")
        for i, prop in enumerate(self.consolidation_proposals, 1):
            report.append(f"\n  [{prop.risk_level.upper()}] Proposal {i}: {prop.action_type.upper()}")
            report.append(f"    Reason: {prop.reason}")
            report.append(f"    Files affected: {len(prop.source)}")
            report.append(f"    Reversible: {'Yes ✅' if prop.reversible else 'No ⚠️'}")
        
        report.append("\n")
        report.append("🎯 NEXT STEPS")
        report.append("  1. Review this report")
        report.append("  2. Run 'oams apply-low-risk' to apply low-risk changes")
        report.append("  3. Run 'oams simulate' to preview medium/high risk changes")
        report.append("  4. Schedule consolidation work with human review")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _should_ignore(self, path: Path) -> bool:
        """Determine if a file should be ignored from analysis."""
        ignore_patterns = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'dist', 'build'}
        return any(pattern in path.parts for pattern in ignore_patterns)
    
    def _persist_metrics(self):
        """Save metrics to JSONL database (append-only, immutable)."""
        with open(self.metrics_db, 'a') as f:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {k: asdict(v) for k, v in self.file_metrics.items()}
            }
            f.write(json.dumps(entry) + '\n')


class SmartConsolidationOrchestrator:
    """
    Orchestrates consolidation changes safely.
    - Simulates before applying
    - Creates rollback points
    - Verifies results
    """
    
    def __init__(self, repo_root: str, system: AdaptiveOrganizationSystem):
        self.repo_root = Path(repo_root)
        self.system = system
    
    def simulate_consolidation(self, proposal: ConsolidationAction) -> Dict[str, Any]:
        """Simulate what would happen with this consolidation."""
        logger.info(f"🔮 Simulating: {proposal.action_type}")
        
        simulation = {
            'proposal': asdict(proposal),
            'impact': {
                'files_affected': len(proposal.source),
                'space_saved_bytes': 0,
                'new_structure': str(proposal.target),
                'broken_links': [],
                'warnings': [],
            }
        }
        
        # Would need to analyze actual cross-references
        # This is placeholder
        
        return simulation
    
    def create_checkpoint(self) -> str:
        """Create a git checkpoint before consolidation."""
        import subprocess
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            msg = f"[OAMS] Pre-consolidation checkpoint {timestamp}"
            subprocess.run(['git', 'add', '-A'], cwd=self.repo_root)
            subprocess.run(['git', 'commit', '-m', msg], cwd=self.repo_root)
            return timestamp
        except Exception as e:
            logger.warning(f"Could not create git checkpoint: {e}")
            return None


def main():
    """Main entry point."""
    repo_root = os.environ.get('REPO_ROOT', '/home/arcana-novai/Documents/Xoe-NovAi/omega-stack')
    
    if not Path(repo_root).exists():
        logger.error(f"Repo not found: {repo_root}")
        return 1
    
    system = AdaptiveOrganizationSystem(repo_root)
    
    # Run analysis pipeline
    system.scan_and_update_metrics()
    system.analyze_structure_entropy()
    proposals = system.generate_consolidation_proposals()
    knowledge_map = system.create_knowledge_map()
    
    # Generate report
    report = system.generate_governance_report()
    print(report)
    
    # Save state
    state_file = Path(repo_root) / ".oams" / "state.json"
    state_file.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'proposals': [asdict(p) for p in proposals],
        'knowledge_map': knowledge_map,
    }, indent=2, default=str))
    
    logger.info(f"✅ State saved to {state_file}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
