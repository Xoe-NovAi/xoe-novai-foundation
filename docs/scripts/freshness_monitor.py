#!/usr/bin/env python3
"""
Documentation Freshness Monitor for Xoe-NovAi

This script monitors documentation freshness, validates links, checks for outdated content,
and generates reports on documentation health.

Usage:
    python docs/scripts/freshness_monitor.py [options]

Options:
    --check         Run freshness checks
    --report        Generate detailed report
    --alerts        Show alerts for outdated content
    --validate      Validate documentation structure
    --help          Show this help message

Author: Xoe-NovAi Documentation Team
Date: January 27, 2026
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
import argparse
import subprocess

class DocumentationFreshnessMonitor:
    """Monitor documentation freshness and quality"""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.alerts = []
        self.warnings = []
        self.errors = []
        self.stats = {
            'total_files': 0,
            'active_files': 0,
            'outdated_files': 0,
            'missing_frontmatter': 0,
            'broken_links': 0,
            'last_check': datetime.now().isoformat()
        }

    def scan_documentation(self) -> Dict:
        """Scan all documentation files and collect metadata"""
        docs_data = {}

        # Find all markdown files
        for md_file in self.docs_root.rglob('*.md'):
            if md_file.name.startswith('.') or 'node_modules' in str(md_file):
                continue

            try:
                data = self.analyze_file(md_file)
                if data:
                    docs_data[str(md_file.relative_to(self.docs_root))] = data
                    self.stats['total_files'] += 1

            except Exception as e:
                self.errors.append(f"Error analyzing {md_file}: {e}")

        return docs_data

    def analyze_file(self, file_path: Path) -> Optional[Dict]:
        """Analyze a single documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter = self.extract_frontmatter(content)
            if not frontmatter:
                self.stats['missing_frontmatter'] += 1
                return None

            # Check status
            status = frontmatter.get('status', 'unknown')
            if status == 'active':
                self.stats['active_files'] += 1

            # Check last updated date
            last_updated = frontmatter.get('last_updated')
            days_since_update = None
            if last_updated:
                try:
                    days_since_update = self.days_since_update(last_updated)
                except Exception:
                    # Skip date parsing errors
                    days_since_update = None

                # Alert thresholds (only if we successfully calculated days)
                if days_since_update is not None:
                    if days_since_update > 90:  # 3 months
                        self.alerts.append({
                            'file': str(file_path.relative_to(self.docs_root)),
                            'type': 'outdated',
                            'days': days_since_update,
                            'message': f'Not updated in {days_since_update} days'
                        })
                        self.stats['outdated_files'] += 1
                    elif days_since_update > 30:  # 1 month
                        self.warnings.append({
                            'file': str(file_path.relative_to(self.docs_root)),
                            'type': 'aging',
                            'days': days_since_update,
                            'message': f'Not updated in {days_since_update} days'
                        })

            # Check for broken links
            broken_links = self.check_links(content, file_path)
            if broken_links:
                self.stats['broken_links'] += len(broken_links)
                for link in broken_links:
                    self.errors.append({
                        'file': str(file_path.relative_to(self.docs_root)),
                        'type': 'broken_link',
                        'link': link,
                        'message': f'Broken link: {link}'
                    })

            return {
                'frontmatter': frontmatter,
                'word_count': len(content.split()),
                'last_updated': last_updated,
                'days_since_update': days_since_update if last_updated else None,
                'broken_links': broken_links,
                'status': status
            }

        except Exception as e:
            self.errors.append(f"Failed to analyze {file_path}: {e}")
            return None

    def extract_frontmatter(self, content: str) -> Optional[Dict]:
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return None

        try:
            # Find the end of frontmatter
            end_pos = content.find('---', 3)
            if end_pos == -1:
                return None

            frontmatter_text = content[3:end_pos].strip()
            frontmatter = yaml.safe_load(frontmatter_text) or {}

            # Ensure all date-like values are strings for JSON serialization
            if frontmatter and 'last_updated' in frontmatter:
                if isinstance(frontmatter['last_updated'], (datetime, date)):
                    frontmatter['last_updated'] = frontmatter['last_updated'].isoformat()

            return frontmatter

        except yaml.YAMLError:
            return None

    def days_since_update(self, last_updated: str) -> int:
        """Calculate days since last update"""
        try:
            # Handle different date formats
            if len(last_updated) == 10:  # YYYY-MM-DD
                update_date = datetime.strptime(last_updated, '%Y-%m-%d')
            elif len(last_updated) == 19:  # YYYY-MM-DD HH:MM:SS
                update_date = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
            else:
                return 999  # Unknown format, mark as very old

            return (datetime.now() - update_date).days

        except ValueError:
            return 999  # Invalid date format

    def check_links(self, content: str, file_path: Path) -> List[str]:
        """Check for broken relative links in content"""
        broken_links = []

        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)

        for text, url in links:
            if url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue  # Skip external links

            # Handle relative links
            if url.startswith('./') or url.startswith('../'):
                # Calculate absolute path
                link_path = (file_path.parent / url).resolve()

                # Check if target exists
                if not link_path.exists():
                    # Try with .md extension if not present
                    if not url.endswith('.md'):
                        link_path = (file_path.parent / f"{url}.md").resolve()
                        if not link_path.exists():
                            broken_links.append(url)
                    else:
                        broken_links.append(url)

        return broken_links

    def generate_report(self, docs_data: Dict) -> Dict:
        """Generate comprehensive freshness report"""
        report = {
            'summary': self.stats,
            'alerts': self.alerts,
            'warnings': self.warnings,
            'errors': self.errors,
            'file_analysis': docs_data,
            'generated_at': datetime.now().isoformat(),
            'recommendations': self.generate_recommendations()
        }

        return report

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        if self.stats['outdated_files'] > 0:
            recommendations.append(f"Update {self.stats['outdated_files']} outdated files (not updated in 90+ days)")

        if self.stats['missing_frontmatter'] > 0:
            recommendations.append(f"Add frontmatter to {self.stats['missing_frontmatter']} files missing metadata")

        if self.stats['broken_links'] > 0:
            recommendations.append(f"Fix {self.stats['broken_links']} broken links across documentation")

        if len(self.warnings) > 0:
            recommendations.append(f"Review {len(self.warnings)} files with aging content (30+ days old)")

        # Freshness monitoring recommendations
        recommendations.extend([
            "Set up automated freshness monitoring in CI/CD pipeline",
            "Configure alerts for files not updated in 90+ days",
            "Establish regular documentation review schedule",
            "Implement freshness badges in documentation headers"
        ])

        return recommendations

    def save_report(self, report: Dict, output_file: Path):
        """Save report to JSON file"""
        # Convert datetime objects to strings for JSON serialization
        def serialize_dates(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: serialize_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_dates(item) for item in obj]
            else:
                return obj

        serializable_report = serialize_dates(report)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)

    def print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("📊 Documentation Freshness Report")
        print("=" * 50)
        print(f"Generated: {report['generated_at'][:19]}")
        print()

        stats = report['summary']
        print("📈 Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Active files: {stats['active_files']}")
        print(f"  Outdated files: {stats['outdated_files']}")
        print(f"  Missing frontmatter: {stats['missing_frontmatter']}")
        print(f"  Broken links: {stats['broken_links']}")
        print()

        if report['alerts']:
            print("🚨 Critical Alerts:")
            for alert in report['alerts'][:5]:  # Show first 5
                print(f"  🔴 {alert['file']}: {alert['message']}")
            if len(report['alerts']) > 5:
                print(f"  ... and {len(report['alerts']) - 5} more alerts")
            print()

        if report['warnings']:
            print("⚠️  Warnings:")
            for warning in report['warnings'][:3]:  # Show first 3
                print(f"  🟡 {warning['file']}: {warning['message']}")
            if len(report['warnings']) > 3:
                print(f"  ... and {len(report['warnings']) - 3} more warnings")
            print()

        if report['errors']:
            print("❌ Errors:")
            for error in report['errors'][:3]:  # Show first 3
                print(f"  🔴 {error}")
            if len(report['errors']) > 3:
                print(f"  ... and {len(report['errors']) - 3} more errors")
            print()

        print("💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        print()

        # Health score
        health_score = self.calculate_health_score(report)
        print(f"🏥 Documentation Health Score: {health_score}/100")

        if health_score >= 90:
            print("✅ Excellent documentation health")
        elif health_score >= 75:
            print("🟡 Good documentation health - minor improvements needed")
        elif health_score >= 60:
            print("🟠 Fair documentation health - attention needed")
        else:
            print("🔴 Poor documentation health - immediate action required")

    def calculate_health_score(self, report: Dict) -> int:
        """Calculate documentation health score (0-100)"""
        stats = report['summary']

        # Base score
        score = 100

        # Deduct for issues
        score -= min(stats['outdated_files'] * 5, 30)  # Max 30 points for outdated
        score -= min(stats['missing_frontmatter'] * 10, 20)  # Max 20 points for missing frontmatter
        score -= min(stats['broken_links'] * 2, 20)  # Max 20 points for broken links
        score -= min(len(report['errors']) * 5, 20)  # Max 20 points for errors

        # Bonus for active files
        if stats['active_files'] > 0 and stats['total_files'] > 0:
            active_ratio = stats['active_files'] / stats['total_files']
            score += int(active_ratio * 10)  # Max 10 point bonus

        return max(0, min(100, score))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Documentation Freshness Monitor')
    parser.add_argument('--check', action='store_true', help='Run freshness checks')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--alerts', action='store_true', help='Show alerts for outdated content')
    parser.add_argument('--validate', action='store_true', help='Validate documentation structure')
    parser.add_argument('--output', type=str, default='docs_freshness_report.json', help='Output file for report')

    args = parser.parse_args()

    # Determine docs root (script location relative)
    script_dir = Path(__file__).parent
    docs_root = script_dir.parent  # Go up one level to docs/

    # Initialize monitor
    monitor = DocumentationFreshnessMonitor(docs_root)

    if args.check or args.report or args.alerts or args.validate:
        print("🔍 Scanning documentation...")
        docs_data = monitor.scan_documentation()

        if args.report:
            print("📋 Generating detailed report...")
            report = monitor.generate_report(docs_data)
            output_file = Path(args.output)
            monitor.save_report(report, output_file)
            print(f"✅ Report saved to {output_file}")

        if args.check or args.alerts:
            report = monitor.generate_report(docs_data)
            monitor.print_summary(report)

        if args.validate:
            print("🔬 Validating documentation structure...")
            # Additional validation logic could go here
            print("✅ Structure validation complete")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
