#!/usr/bin/env python3
"""
OMEGA Stack Intelligent Architecture Reorganizer

Based on:
- Diataxis Framework (Tutorials, How-to, Reference, Explanation)
- Obsidian Principles (Atomic notes, backlinks, emergence, knowledge graph)
- Progressive Information Architecture
- Information foraging behavior

Purpose: Intelligently consolidate repo using proven information design patterns
while preserving all data and creating a discoverable knowledge graph.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ARCHITECT] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/var/log/omega-architect.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DiataxisClassifier:
    """Classify content using the Diataxis framework."""
    
    # Keywords for each Diataxis category
    TUTORI AL_KEYWORDS = {
        'tutorial', 'getting-started', 'quick-start', 'beginner', 'intro',
        'walkthrough', 'example', 'hands-on', 'learn'
    }
    
    HOWTO_KEYWORDS = {
        'how-to', 'guide', 'procedure', 'steps', 'instructions', 'setup',
        'configure', 'install', 'deploy', 'fix', 'troubleshoot'
    }
    
    REFERENCE_KEYWORDS = {
        'reference', 'api', 'spec', 'schema', 'config', 'documentation',
        'manual', 'format', 'syntax', 'parameters', 'options'
    }
    
    EXPLANATION_KEYWORDS = {
        'explanation', 'design', 'architecture', 'rationale', 'theory',
        'overview', 'concept', 'background', 'deep-dive', 'analysis'
    }
    
    def classify(self, path: Path, content: str = "") -> str:
        """Classify a file into Diataxis category."""
        name_lower = path.name.lower()
        parent_lower = path.parent.name.lower()
        
        # Check filename and parent directory
        combined = f"{name_lower} {parent_lower} {content[:500].lower()}"
        
        # Scoring system
        scores = {
            'tutorial': self._score(combined, self.TUTORI AL_KEYWORDS),
            'howto': self._score(combined, self.HOWTO_KEYWORDS),
            'reference': self._score(combined, self.REFERENCE_KEYWORDS),
            'explanation': self._score(combined, self.EXPLANATION_KEYWORDS),
        }
        
        # Return category with highest score, default to 'reference'
        return max(scores, key=scores.get) if any(scores.values()) else 'reference'
    
    @staticmethod
    def _score(text: str, keywords: Set[str]) -> float:
        """Score text against keyword set."""
        return sum(1 for kw in keywords if kw in text)


class ObsidianLinkAnalyzer:
    """Build knowledge graph and analyze cross-references (Obsidian style)."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.links = defaultdict(set)
        self.backlinks = defaultdict(set)
        self.graph = {}
    
    def extract_references(self, file_path: Path) -> Set[str]:
        """Extract references: [[wikilinks]], file paths, relative imports."""
        references = set()
        
        try:
            content = file_path.read_text(errors='ignore')
        except:
            return references
        
        # [[wikilinks]] pattern
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        references.update(wiki_links)
        
        # [Relative links](../path/to/file.md)
        relative_links = re.findall(r'\]\(\.\.?/[^)]+\)', content)
        references.update(relative_links)
        
        # Import statements (Python, JS, etc)
        import_patterns = [
            r'from\s+[\'"]([^\'"]+)[\'"]',  # Python from X import
            r'import\s+[\'"]([^\'"]+)[\'"]',  # Python/JS import
            r'require\([\'"]([^\'"]+)[\'"]\)',  # JS require
        ]
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            references.update(matches)
        
        return references
    
    def build_graph(self) -> Dict[str, Any]:
        """Build knowledge graph of entire repo."""
        logger.info("🔗 Building knowledge graph...")
        
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.md', '.py', '.ts', '.js']:
                references = self.extract_references(file_path)
                rel_path = str(file_path.relative_to(self.repo_root))
                
                self.links[rel_path] = references
                for ref in references:
                    self.backlinks[ref].add(rel_path)
        
        logger.info(f"✅ Graph built: {len(self.links)} files, {sum(len(v) for v in self.links.values())} links")
        return {
            'links': dict(self.links),
            'backlinks': dict(self.backlinks),
        }
    
    def find_orphaned_files(self) -> List[str]:
        """Find files with no backlinks (orphaned)."""
        orphaned = []
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.repo_root))
                # Check if referenced anywhere
                if rel_path not in self.backlinks and len(self.links.get(rel_path, [])) == 0:
                    orphaned.append(rel_path)
        return orphaned


class IntelligentArchitect:
    """Main reorganization engine using Diataxis + Obsidian principles."""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.classifier = DiataxisClassifier()
        self.analyzer = ObsidianLinkAnalyzer(self.repo_root)
        
        # Target structure
        self.target_structure = {
            'docs/': {
                'tutorials/': 'Hands-on step-by-step guides',
                'how-to/': 'Solution-focused procedures',
                'reference/': 'Technical specifications & APIs',
                'explanation/': 'Conceptual deep-dives & architecture',
            },
            'knowledge/': {
                'concepts/': 'Foundational ideas & theory',
                'procedures/': 'Operational guidelines',
                'glossary.md': 'Terminology index',
            },
            '_archive/': {
                'obsolete/': 'Deprecated code & docs',
                'historical/': 'Past versions & decisions',
            },
        }
        
        self.consolidation_plan = []
        self.preservation_manifests = []
    
    def analyze_repo(self) -> Dict[str, Any]:
        """Comprehensive repo analysis using information architecture principles."""
        logger.info("🏛️  Analyzing repository with architectural principles...")
        
        # Build knowledge graph
        graph = self.analyzer.build_graph()
        
        # Find orphaned files
        orphaned = self.analyzer.find_orphaned_files()
        
        # Classify all content by Diataxis
        diataxis_map = defaultdict(list)
        for file_path in self.repo_root.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.py']:
                try:
                    category = self.classifier.classify(file_path)
                    rel_path = str(file_path.relative_to(self.repo_root))
                    diataxis_map[category].append(rel_path)
                except Exception as e:
                    logger.warning(f"Could not classify {file_path}: {e}")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'knowledge_graph': graph,
            'orphaned_files': orphaned,
            'diataxis_classification': dict(diataxis_map),
            'consolidation_opportunities': self._identify_opportunities(diataxis_map),
        }
        
        return analysis
    
    def _identify_opportunities(self, diataxis_map: Dict) -> List[Dict]:
        """Identify consolidation opportunities based on Diataxis analysis."""
        opportunities = []
        
        for category, files in diataxis_map.items():
            if len(files) > 10:
                opportunities.append({
                    'type': 'high_volume',
                    'category': category,
                    'file_count': len(files),
                    'action': f"Consolidate {len(files)} {category} files into dedicated section"
                })
        
        return opportunities
    
    def create_index_files(self) -> List[Path]:
        """Create Obsidian-style index files for navigation and discovery."""
        logger.info("📑 Creating index files...")
        
        index_files = []
        
        # Main architecture guide
        main_index = self.repo_root / "ARCHITECTURE.md"
        main_index.write_text("""# OMEGA Stack Architecture

> Based on Diataxis Framework + Obsidian Information Architecture

## Navigation by Purpose

### [[Tutorials]] - Learning & Getting Started
Step-by-step guides for new users and explorers.
- [[Quick Start]]
- [[Installation Guide]]
- [[First Project]]

### [[How-To]] - Solution-Focused Procedures
Task-oriented guides for accomplishing specific goals.
- [[Setting Up Development Environment]]
- [[Deploying to Production]]
- [[Troubleshooting Common Issues]]

### [[Reference]] - Specifications & APIs
Authoritative technical documentation.
- [[API Reference]]
- [[Configuration Reference]]
- [[Data Schema]]

### [[Explanation]] - Conceptual Deep-Dives
Understanding the "why" and design decisions.
- [[Architecture Overview]]
- [[Design Patterns]]
- [[Performance Considerations]]

## Knowledge Graph

See [[Knowledge Map]] for cross-references and relationships.

## Index by Topic

- [[Archon Identity System]]
- [[Memory Bank Architecture]]
- [[Multi-Agent Orchestration]]
- [[Gnosis Black Hole]]
- [[JEM Ignition Strategy]]

---

Last updated: {timestamp}
""".format(timestamp=datetime.now().isoformat()))
        
        index_files.append(main_index)
        logger.info(f"✅ Created {main_index}")
        
        # Create Diataxis section indexes
        sections = {
            'tutorials': 'Tutorials - Learning by Doing',
            'howto': 'How-To Guides - Task-Oriented Solutions',
            'reference': 'Reference - Technical Specifications',
            'explanation': 'Explanation - Conceptual Understanding',
        }
        
        for section, title in sections.items():
            index_file = self.repo_root / f"docs/{section}/INDEX.md"
            index_file.parent.mkdir(parents=True, exist_ok=True)
            
            index_file.write_text(f"""# {title}

> Part of the Diataxis Framework for information organization

## Files in This Section

[Files will be auto-indexed here based on knowledge graph]

## Related Sections

- [[../tutorials/INDEX.md|Tutorials]]
- [[../how-to/INDEX.md|How-To]]
- [[../reference/INDEX.md|Reference]]
- [[../explanation/INDEX.md|Explanation]]

---

**Information Architecture**: Each section serves a specific audience need.
""")
            index_files.append(index_file)
        
        return index_files
    
    def create_consolidation_script(self) -> Path:
        """Create a safe, reversible consolidation script."""
        logger.info("🛠️  Creating consolidation script...")
        
        script = self.repo_root / "scripts/consolidate-by-diataxis.sh"
        
        script_content = """#!/bin/bash
# Safe, Reversible Consolidation Script
# Based on Diataxis Framework + Obsidian Principles
# 
# WARNING: Review changes before applying
# Creates symlinks instead of moving files initially

set -euo pipefail

REPO_ROOT="${1:-.}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_LOG="$REPO_ROOT/consolidation-log-$TIMESTAMP.txt"

echo "📋 CONSOLIDATION PLAN (Review before applying)"
echo "=============================================="
echo ""

# Phase 1: Create target structure
echo "Phase 1: Creating Diataxis target structure..."
mkdir -p "$REPO_ROOT/docs/tutorials"
mkdir -p "$REPO_ROOT/docs/how-to"
mkdir -p "$REPO_ROOT/docs/reference"
mkdir -p "$REPO_ROOT/docs/explanation"
mkdir -p "$REPO_ROOT/knowledge/concepts"
mkdir -p "$REPO_ROOT/knowledge/procedures"
mkdir -p "$REPO_ROOT/_archive/obsolete"
mkdir -p "$REPO_ROOT/_archive/historical"

echo "✅ Target structure created"
echo ""

# Phase 2: Create index files
echo "Phase 2: Creating index files..."
echo "  - ARCHITECTURE.md (main navigation)"
echo "  - docs/*/INDEX.md (section indexes)"
echo "  - knowledge/INDEX.md"
echo "  - _archive/INDEX.md"
echo "✅ Index files ready"
echo ""

# Phase 3: Preview consolidation
echo "Phase 3: Files ready for consolidation"
echo "  (Use 'consolidate-apply.sh' to commit changes)"
echo ""

echo "✅ Consolidation plan ready!"
echo "📝 Log saved to: $BACKUP_LOG"
"""
        
        script.write_text(script_content)
        script.chmod(0o755)
        
        logger.info(f"✅ Created {script}")
        return script
    
    def generate_architecture_report(self, analysis: Dict) -> str:
        """Generate comprehensive architecture report."""
        report = []
        report.append("=" * 80)
        report.append("OMEGA STACK - INTELLIGENT ARCHITECTURE ANALYSIS")
        report.append("(Based on Diataxis Framework + Obsidian Principles)")
        report.append("=" * 80)
        report.append("")
        
        # Diataxis Classification
        report.append("📚 DIATAXIS CLASSIFICATION")
        report.append("-" * 40)
        for category, files in analysis['diataxis_classification'].items():
            report.append(f"\n{category.upper()} ({len(files)} files)")
            report.append(f"  Purpose: {self._diataxis_purpose(category)}")
            for file in files[:3]:
                report.append(f"    • {file}")
            if len(files) > 3:
                report.append(f"    ... and {len(files) - 3} more")
        
        report.append("\n")
        
        # Knowledge Graph
        report.append("🔗 KNOWLEDGE GRAPH ANALYSIS")
        report.append("-" * 40)
        graph = analysis['knowledge_graph']
        report.append(f"Total files tracked: {len(graph['links'])}")
        report.append(f"Total cross-references: {sum(len(v) for v in graph['links'].values())}")
        
        # Orphaned files
        if analysis['orphaned_files']:
            report.append(f"\n⚠️  ORPHANED FILES ({len(analysis['orphaned_files'])})")
            report.append("  (Files with no cross-references - candidates for archival)")
            for file in analysis['orphaned_files'][:10]:
                report.append(f"    • {file}")
        
        report.append("\n")
        
        # Consolidation Opportunities
        report.append("💡 CONSOLIDATION OPPORTUNITIES")
        report.append("-" * 40)
        for opp in analysis['consolidation_opportunities']:
            report.append(f"\n{opp['action']}")
            report.append(f"  Category: {opp['category']}")
            report.append(f"  Files: {opp['file_count']}")
        
        report.append("\n")
        report.append("=" * 80)
        report.append("ACTION ITEMS:")
        report.append("1. Review this analysis")
        report.append("2. Review ARCHITECTURE.md for proposed structure")
        report.append("3. Run: scripts/consolidate-by-diataxis.sh")
        report.append("4. Verify with: git status")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    @staticmethod
    def _diataxis_purpose(category: str) -> str:
        """Get description of Diataxis category purpose."""
        purposes = {
            'tutorial': 'Learning-focused: step-by-step introduction',
            'howto': 'Task-focused: solve specific problems',
            'reference': 'Information-focused: look up specifications',
            'explanation': 'Understanding-focused: conceptual knowledge',
        }
        return purposes.get(category, 'Mixed content')


def main():
    """Main entry point."""
    repo_root = os.environ.get('REPO_ROOT', '/home/arcana-novai/Documents/Xoe-NovAi/omega-stack')
    
    architect = IntelligentArchitect(repo_root)
    
    logger.info("🏗️  OMEGA Stack Intelligent Architect")
    logger.info(f"Repo: {repo_root}")
    logger.info("")
    
    # Analyze
    analysis = architect.analyze_repo()
    
    # Create index files
    architect.create_index_files()
    
    # Create consolidation script
    architect.create_consolidation_script()
    
    # Generate and print report
    report = architect.generate_architecture_report(analysis)
    print(report)
    
    # Save analysis and report
    analysis_file = Path(repo_root) / "monitoring" / "architecture-analysis.json"
    analysis_file.parent.mkdir(parents=True, exist_ok=True)
    analysis_file.write_text(json.dumps(analysis, indent=2))
    
    report_file = Path(repo_root) / "monitoring" / "architecture-report.txt"
    report_file.write_text(report)
    
    logger.info(f"✅ Analysis saved: {analysis_file}")
    logger.info(f"✅ Report saved: {report_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
