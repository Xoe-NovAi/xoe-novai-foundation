#!/usr/bin/env python3
"""
Xoe-NovAi Documentation Research Validator
Automated validation of Grok v5 research integration across all documentation.

Features:
- Comprehensive research keyword validation
- Research area coverage assessment
- Automated compliance checking
- Integration gap identification

Author: Xoe-NovAi Documentation Enhancement Team
Date: January 27, 2026
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import re

class ResearchValidator:
    """Automated validation of Grok v5 research integration."""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.research_requirements = self._load_research_requirements()

    def _load_research_requirements(self) -> Dict[str, Any]:
        """Load comprehensive Grok v5 research requirements."""

        return {
            'vulkan': {
                'display_name': 'Vulkan-Only Research',
                'priority': 'critical',
                'keywords': [
                    'vulkan', 'mesa 25.3', 'agesa', 'mlock', 'mmap',
                    'vulkan-only', 'gpu acceleration', '20-70% gains',
                    '92-95% stability', 'hybrid acceleration'
                ],
                'required_context': [
                    'Mesa 25.3+ Vulkan drivers',
                    'AGESA 1.2.0.8+ firmware validation',
                    'mlock/mmap for <6GB enforcement',
                    'CPU+iGPU inference patterns'
                ],
                'critical_documents': ['architecture', 'development', 'design']
            },
            'kokoro': {
                'display_name': 'Kokoro v2 TTS',
                'priority': 'high',
                'keywords': [
                    'kokoro v2', 'multilingual', 'prosody', '1.2-1.8x',
                    'voice synthesis', 'tts', 'text-to-speech',
                    'naturalness improvement', 'voice response'
                ],
                'required_context': [
                    'EN/FR/KR/JP/CN language support',
                    '1.2-1.8x naturalness improvement',
                    '200-500ms latency with batching',
                    'Integrated voice RAG capabilities'
                ],
                'critical_documents': ['voice', 'interface', 'deployment']
            },
            'qdrant': {
                'display_name': 'Qdrant 1.9 Agentic Features',
                'priority': 'high',
                'keywords': [
                    'qdrant 1.9', 'agentic', '+45% recall', 'hybrid search',
                    'vector database', 'local performance', '<75ms query',
                    'faiss migration', 'dense+sparse'
                ],
                'required_context': [
                    '+45% recall through intelligent filtering',
                    'Dense+sparse vector combination',
                    '<75ms query performance locally',
                    'FAISS to Qdrant transition planning'
                ],
                'critical_documents': ['architecture', 'development', 'deployment']
            },
            'wasm': {
                'display_name': 'WASM Component Model',
                'priority': 'medium',
                'keywords': [
                    'wasm component', '+30% efficiency', 'interop', 'composability',
                    'portability', 'plugin architecture', 'sandboxing',
                    'cross-environment', 'secure execution'
                ],
                'required_context': [
                    '+30% efficiency through interop',
                    'Cross-environment compatibility',
                    'Extensible component system',
                    'Secure execution environments'
                ],
                'critical_documents': ['architecture', 'plugin', 'development']
            },
            'circuit_breaker': {
                'display_name': 'Circuit Breaker Architecture',
                'priority': 'high',
                'keywords': [
                    'circuit breaker', 'chaos engineering', 'fault tolerance',
                    'resilience', 'fallback mechanisms', 'load testing',
                    'error handling', 'graceful degradation'
                ],
                'required_context': [
                    'Automated chaos testing integration',
                    '+300% improvement in fault tolerance',
                    'Comprehensive fallback mechanisms',
                    'Load testing and performance validation'
                ],
                'critical_documents': ['architecture', 'testing', 'operations']
            },
            'performance': {
                'display_name': 'Build Performance Optimization',
                'priority': 'medium',
                'keywords': [
                    'build performance', 'smart caching', 'parallel processing',
                    '95% faster builds', 'interactive progress', 'optimization',
                    'cache invalidation', 'enterprise-grade'
                ],
                'required_context': [
                    'Smart caching and parallel processing',
                    '95% faster build times',
                    'Interactive progress bars',
                    'Enterprise-grade build reliability'
                ],
                'critical_documents': ['development', 'build', 'deployment']
            }
        }

    def validate_research_integration(self) -> Dict[str, Any]:
        """Comprehensive research integration validation."""

        print("🔬 Validating Grok v5 research integration...")

        validation = {
            'timestamp': datetime.now().isoformat(),
            'total_documents': 0,
            'research_areas': {},
            'compliance_score': 0,
            'critical_gaps': [],
            'integration_status': {},
            'recommendations': []
        }

        # Analyze all documents
        for md_file in self.docs_root.rglob("*.md"):
            if self._should_validate(md_file):
                doc_validation = self._validate_document_research(md_file)
                validation['total_documents'] += 1

                # Aggregate research area coverage
                for area, coverage in doc_validation['research_coverage'].items():
                    if area not in validation['research_areas']:
                        validation['research_areas'][area] = {
                            'total_documents': 0,
                            'covered_documents': 0,
                            'total_references': 0,
                            'critical_gaps': []
                        }

                    validation['research_areas'][area]['total_documents'] += 1
                    if coverage['has_references']:
                        validation['research_areas'][area]['covered_documents'] += 1
                        validation['research_areas'][area]['total_references'] += coverage['reference_count']

                    if coverage['critical_gaps']:
                        validation['research_areas'][area]['critical_gaps'].extend(coverage['critical_gaps'])

        # Calculate compliance scores
        validation['compliance_score'] = self._calculate_compliance_score(validation)

        # Identify critical gaps
        validation['critical_gaps'] = self._identify_critical_gaps(validation)

        # Generate recommendations
        validation['recommendations'] = self._generate_recommendations(validation)

        # Determine integration status
        validation['integration_status'] = self._assess_integration_status(validation)

        print(f"✅ Research validation complete: {validation['total_documents']} documents analyzed")
        return validation

    def _should_validate(self, file_path: Path) -> bool:
        """Determine if document should be validated."""

        # Skip archive files
        if "archive" in str(file_path):
            return False

        # Skip special system files
        special_files = ["README.md", "index.html", "index.json", "search_index.json"]
        if file_path.name in special_files:
            return False

        # Skip script files
        if "scripts" in str(file_path):
            return False

        return True

    def _validate_document_research(self, file_path: Path) -> Dict[str, Any]:
        """Validate research integration in a single document."""

        doc_validation = {
            'file_path': str(file_path.relative_to(self.docs_root)),
            'research_coverage': {},
            'total_references': 0,
            'critical_gaps': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # Extract frontmatter to determine category
            frontmatter = self._extract_frontmatter(file_path)
            category = frontmatter.get('category', 'uncategorized')

            # Check each research area
            for area, requirements in self.research_requirements.items():
                coverage = {
                    'has_references': False,
                    'reference_count': 0,
                    'critical_gaps': [],
                    'is_critical': category in requirements['critical_documents']
                }

                # Count keyword matches
                keyword_matches = 0
                for keyword in requirements['keywords']:
                    matches = len(re.findall(re.escape(keyword.lower()), content))
                    if matches > 0:
                        keyword_matches += matches
                        coverage['has_references'] = True

                coverage['reference_count'] = keyword_matches
                doc_validation['total_references'] += keyword_matches

                # Check for critical context gaps
                if coverage['is_critical']:
                    for context in requirements['required_context']:
                        context_lower = context.lower()
                        if context_lower not in content:
                            coverage['critical_gaps'].append(context)

                doc_validation['research_coverage'][area] = coverage

                # Add critical gaps to document level
                if coverage['critical_gaps']:
                    doc_validation['critical_gaps'].extend([
                        f"{area}: {gap}" for gap in coverage['critical_gaps']
                    ])

        except Exception as e:
            doc_validation['error'] = str(e)

        return doc_validation

    def _extract_frontmatter(self, file_path: Path) -> Dict[str, Any]:
        """Extract YAML frontmatter from document."""

        frontmatter = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = yaml.safe_load(parts[1]) or {}

        except Exception:
            pass

        return frontmatter

    def _calculate_compliance_score(self, validation: Dict[str, Any]) -> float:
        """Calculate overall research compliance score."""

        if validation['total_documents'] == 0:
            return 0.0

        total_score = 0
        area_count = len(self.research_requirements)

        for area, stats in validation['research_areas'].items():
            if stats['total_documents'] > 0:
                # Base coverage score
                coverage_score = (stats['covered_documents'] / stats['total_documents']) * 100

                # Bonus for multiple references
                reference_bonus = min(stats['total_references'] / stats['covered_documents'], 50) if stats['covered_documents'] > 0 else 0

                # Penalty for critical gaps
                gap_penalty = len(stats['critical_gaps']) * 5

                area_score = max(0, coverage_score + reference_bonus - gap_penalty)
                total_score += area_score

        return total_score / area_count

    def _identify_critical_gaps(self, validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical research integration gaps."""

        critical_gaps = []

        for area, stats in validation['research_areas'].items():
            requirements = self.research_requirements[area]

            # Check coverage gaps
            coverage_percentage = (stats['covered_documents'] / stats['total_documents']) * 100 if stats['total_documents'] > 0 else 0

            if coverage_percentage < 50 and requirements['priority'] in ['critical', 'high']:
                critical_gaps.append({
                    'type': 'coverage_gap',
                    'area': area,
                    'severity': requirements['priority'],
                    'description': f"Only {coverage_percentage:.1f}% of documents cover {requirements['display_name']}",
                    'impact': f"{stats['total_documents'] - stats['covered_documents']} documents missing {area} references"
                })

            # Check critical context gaps
            if stats['critical_gaps']:
                critical_gaps.append({
                    'type': 'context_gap',
                    'area': area,
                    'severity': 'high',
                    'description': f"Critical context missing in {area} documentation",
                    'missing_context': stats['critical_gaps'][:5]  # Limit to first 5
                })

        return critical_gaps

    def _generate_recommendations(self, validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable research integration recommendations."""

        recommendations = []

        # Priority-based recommendations
        for area, requirements in self.research_requirements.items():
            stats = validation['research_areas'].get(area, {})

            if stats.get('covered_documents', 0) < stats.get('total_documents', 0) * 0.5:
                priority = "critical" if requirements['priority'] == 'critical' else "high"

                recommendations.append({
                    'priority': priority,
                    'area': area,
                    'title': f"Improve {requirements['display_name']} coverage",
                    'description': f"Only {stats.get('covered_documents', 0)} of {stats.get('total_documents', 0)} documents reference {area}",
                    'actions': [
                        f"Add {area} references to {requirements['critical_documents']} documents",
                        f"Include key findings: {', '.join(requirements['required_context'][:3])}",
                        f"Update category README files with {area} integration notes"
                    ]
                })

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations[:10]  # Limit to top 10 recommendations

    def _assess_integration_status(self, validation: Dict[str, Any]) -> Dict[str, str]:
        """Assess overall research integration status."""

        status = {}

        # Overall status
        score = validation['compliance_score']
        if score >= 80:
            status['overall'] = 'excellent'
        elif score >= 60:
            status['overall'] = 'good'
        elif score >= 40:
            status['overall'] = 'needs_improvement'
        else:
            status['overall'] = 'critical'

        # Area-specific status
        for area in self.research_requirements.keys():
            stats = validation['research_areas'].get(area, {})
            coverage = (stats.get('covered_documents', 0) / stats.get('total_documents', 1)) * 100

            if coverage >= 70:
                status[area] = 'well_integrated'
            elif coverage >= 40:
                status[area] = 'partially_integrated'
            else:
                status[area] = 'needs_attention'

        return status

    def generate_report(self, validation: Dict[str, Any]) -> str:
        """Generate comprehensive research validation report."""

        report = []
        report.append("# 🔬 Grok v5 Research Integration Validation Report")
        report.append(f"**Date:** {validation['timestamp']}")
        report.append(f"**Documents Analyzed:** {validation['total_documents']}")
        report.append("")

        # Executive Summary
        report.append("## 📈 Executive Summary")
        score = validation['compliance_score']
        status = validation['integration_status']['overall']

        status_emoji = {
            'excellent': '🟢',
            'good': '🟡',
            'needs_improvement': '🟠',
            'critical': '🔴'
        }.get(status, '⚪')

        report.append(f"- **Compliance Score:** {score:.1f}% {status_emoji}")
        report.append(f"- **Integration Status:** {status.replace('_', ' ').title()}")
        report.append(f"- **Research Areas:** {len(self.research_requirements)}")
        report.append("")

        # Research Area Status
        report.append("## 🔬 Research Area Coverage")
        for area, requirements in self.research_requirements.items():
            stats = validation['research_areas'].get(area, {})
            coverage = (stats.get('covered_documents', 0) / stats.get('total_documents', 1)) * 100
            status = validation['integration_status'].get(area, 'unknown')

            status_emoji = {
                'well_integrated': '🟢',
                'partially_integrated': '🟡',
                'needs_attention': '🔴'
            }.get(status, '⚪')

            report.append(f"### {requirements['display_name']} {status_emoji}")
            report.append(f"- **Coverage:** {coverage:.1f}% ({stats.get('covered_documents', 0)}/{stats.get('total_documents', 0)} documents)")
            report.append(f"- **References:** {stats.get('total_references', 0)} total")
            report.append(f"- **Priority:** {requirements['priority'].title()}")

            if stats.get('critical_gaps'):
                report.append(f"- **Critical Gaps:** {len(stats['critical_gaps'])}")
                for gap in stats['critical_gaps'][:3]:
                    report.append(f"  - {gap}")

            report.append("")

        # Critical Gaps
        if validation['critical_gaps']:
            report.append("## 🚨 Critical Integration Gaps")
            for gap in validation['critical_gaps']:
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(gap['severity'], "⚪")
                report.append(f"### {severity_emoji} {gap['area'].title()}: {gap['type'].replace('_', ' ').title()}")
                report.append(f"**{gap['description']}**")
                if 'missing_context' in gap:
                    report.append("**Missing Context:**")
                    for context in gap['missing_context']:
                        report.append(f"- {context}")
                report.append("")

        # Recommendations
        if validation['recommendations']:
            report.append("## 💡 Integration Recommendations")
            for rec in validation['recommendations']:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(rec['priority'], "⚪")
                report.append(f"### {priority_emoji} {rec['title']}")
                report.append(f"**{rec['description']}**")
                report.append("")
                for action in rec['actions']:
                    report.append(f"- {action}")
                report.append("")

        # Next Steps
        report.append("## 🚀 Next Steps")
        report.append("1. **Address Critical Gaps:** Update high-priority documents with missing research context")
        report.append("2. **Expand Coverage:** Add research references to uncovered documents")
        report.append("3. **Verify Integration:** Re-run validation after updates")
        report.append("4. **Monitor Progress:** Regular assessment of research alignment")
        report.append("5. **Update Standards:** Incorporate new research findings as they emerge")
        report.append("")

        return "\n".join(report)

def main():
    """Main research validation execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Xoe-NovAi Documentation Research Validator")
    parser.add_argument("--validate", action="store_true", help="Run complete research validation")
    parser.add_argument("--audit", action="store_true", help="Run quick research audit")
    parser.add_argument("--export", type=str, help="Export validation results to JSON")

    args = parser.parse_args()

    docs_root = Path("docs/")
    validator = ResearchValidator(docs_root)

    if args.validate or args.audit:
        print("🔬 Starting Grok v5 research validation...")
        validation = validator.validate_research_integration()

        # Generate and display report
        report = validator.generate_report(validation)
        print("\n" + "="*100)
        print(report)
        print("="*100)

        # Export if requested
        if args.export:
            export_path = Path(args.export)
            try:
                with open(export_path, 'w') as f:
                    json.dump(validation, f, indent=2, default=str)
                print(f"💾 Validation exported to: {export_path}")
            except Exception as e:
                print(f"❌ Failed to export validation: {e}")

        # Save report to docs directory
        report_path = docs_root / "research-validation-report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📋 Report saved to: {report_path}")

    else:
        print("Usage: python research_validator.py [--validate|--audit] [--export FILE]")
        print("  --validate: Run complete research integration validation")
        print("  --audit: Run quick research audit with report")
        print("  --export: Export validation results to JSON file")

if __name__ == "__main__":
    main()
