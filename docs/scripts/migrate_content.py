#!/usr/bin/env python3
"""
Xoe-NovAi Documentation Content Migration Script
Migrates existing documentation to the new numbered category structure.

New Structure:
├── 01-getting-started/     # Sequential onboarding (1→2→3→4)
├── 02-development/         # Development workflows
├── 03-architecture/        # System architecture
├── 04-operations/          # Operational procedures
├── 05-governance/          # Policies and standards
└── 06-meta/               # Documentation system itself

Author: Xoe-NovAi Documentation Enhancement Team
Date: January 27, 2026
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re

class ContentMigrator:
    """Automated content migration to new category structure."""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.category_mapping = self.get_category_mapping()
        self.migration_log = []

    def get_category_mapping(self) -> Dict[str, str]:
        """Define mapping from old categories to new numbered structure."""

        return {
            # Getting Started (01)
            "getting-started": "01-getting-started",
            "quick-start": "01-getting-started",
            "beginner": "01-getting-started",
            "overview": "01-getting-started",
            "introduction": "01-getting-started",

            # Development (02)
            "development": "02-development",
            "howto": "02-development",
            "setup": "02-development",
            "installation": "02-development",
            "configuration": "02-development",
            "deployment": "02-development",
            "build": "02-development",
            "testing": "02-development",
            "debugging": "02-development",

            # Architecture (03)
            "architecture": "03-architecture",
            "design": "03-architecture",
            "reference": "03-architecture",
            "blueprint": "03-architecture",
            "technical": "03-architecture",
            "system": "03-architecture",
            "infrastructure": "03-architecture",

            # Operations (04)
            "operations": "04-operations",
            "runbooks": "04-operations",
            "monitoring": "04-operations",
            "maintenance": "04-operations",
            "troubleshooting": "04-operations",
            "incident": "04-operations",
            "performance": "04-operations",

            # Governance (05)
            "policies": "05-governance",
            "policy": "05-governance",
            "standards": "05-governance",
            "compliance": "05-governance",
            "governance": "05-governance",
            "security": "05-governance",
            "ownership": "05-governance",

            # Meta (06)
            "meta": "06-meta",
            "documentation": "06-meta",
            "tools": "06-meta",
            "automation": "06-meta",
            "index": "06-meta",
            "search": "06-meta"
        }

    def analyze_current_structure(self) -> Dict[str, Any]:
        """Analyze current documentation structure."""

        analysis = {
            "total_files": 0,
            "categories_found": {},
            "uncategorized": [],
            "migration_candidates": {},
            "issues": []
        }

        for md_file in self.docs_root.rglob("*.md"):
            if self._should_analyze(md_file):
                analysis["total_files"] += 1

                category = self._determine_category(md_file)
                if category:
                    if category not in analysis["categories_found"]:
                        analysis["categories_found"][category] = []
                    analysis["categories_found"][category].append(str(md_file.relative_to(self.docs_root)))
                else:
                    analysis["uncategorized"].append(str(md_file.relative_to(self.docs_root)))

        # Generate migration plan
        analysis["migration_candidates"] = self._generate_migration_plan(analysis)

        return analysis

    def _should_analyze(self, file_path: Path) -> bool:
        """Determine if file should be analyzed for migration."""

        # Skip archive files
        if "archive" in str(file_path):
            return False

        # Skip special files
        special_files = ["README.md", "index.html", "index.json", "search_index.json"]
        if file_path.name in special_files:
            return False

        # Skip script files
        if "scripts" in str(file_path):
            return False

        return True

    def _determine_category(self, file_path: Path) -> str:
        """Determine appropriate category for a file."""

        # First, check frontmatter category
        frontmatter_category = self._extract_frontmatter_category(file_path)
        if frontmatter_category and frontmatter_category in self.category_mapping:
            return self.category_mapping[frontmatter_category]

        # Then check folder-based categorization
        folder_category = self._determine_folder_category(file_path)
        if folder_category:
            return folder_category

        # Finally, check filename/content-based categorization
        content_category = self._determine_content_category(file_path)
        if content_category:
            return content_category

        return None

    def _extract_frontmatter_category(self, file_path: Path) -> str:
        """Extract category from YAML frontmatter."""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        return frontmatter.get("category", "").lower()
                    except yaml.YAMLError:
                        pass

        except Exception:
            pass

        return None

    def _determine_folder_category(self, file_path: Path) -> str:
        """Determine category based on folder structure."""

        path_parts = file_path.relative_to(self.docs_root).parts

        folder_mappings = {
            "howto": "02-development",
            "design": "03-architecture",
            "reference": "03-architecture",
            "runbooks": "04-operations",
            "policies": "05-governance",
            "releases": "05-governance",
            "implementation": "02-development",
            "enhancements": "03-architecture"
        }

        for part in path_parts[:-1]:  # Exclude filename
            if part in folder_mappings:
                return folder_mappings[part]

        return None

    def _determine_content_category(self, file_path: Path) -> str:
        """Determine category based on file content and naming."""

        filename = file_path.name.lower()
        filepath_str = str(file_path).lower()

        # Keyword-based categorization
        keyword_mappings = {
            "01-getting-started": [
                "getting.started", "beginner", "quick.start", "overview",
                "introduction", "first", "welcome", "start"
            ],
            "02-development": [
                "setup", "install", "build", "deploy", "test", "debug",
                "develop", "workflow", "configuration", "howto", "guide"
            ],
            "03-architecture": [
                "architecture", "design", "system", "blueprint", "technical",
                "reference", "api", "infrastructure", "pattern"
            ],
            "04-operations": [
                "runbook", "monitor", "maintenance", "troubleshoot", "incident",
                "performance", "operations", "admin", "manage"
            ],
            "05-governance": [
                "policy", "standard", "compliance", "governance", "security",
                "ownership", "guideline", "procedure", "rule"
            ],
            "06-meta": [
                "documentation", "meta", "tool", "automation", "index", "search",
                "validate", "migrate", "organize"
            ]
        }

        # Check filename and path for keywords
        for category, keywords in keyword_mappings.items():
            for keyword in keywords:
                if keyword.replace(".", " ") in filepath_str or keyword in filename:
                    return category

        return None

    def _generate_migration_plan(self, analysis: Dict) -> Dict[str, List[str]]:
        """Generate detailed migration plan."""

        migration_plan = {}

        # Process categorized files
        for category, files in analysis["categories_found"].items():
            if category not in migration_plan:
                migration_plan[category] = []
            migration_plan[category].extend(files)

        # Process uncategorized files with suggestions
        for file_path in analysis["uncategorized"]:
            suggested_category = self._suggest_category_for_file(file_path)
            if suggested_category:
                if suggested_category not in migration_plan:
                    migration_plan[suggested_category] = []
                migration_plan[suggested_category].append(f"{file_path} (suggested)")

        return migration_plan

    def _suggest_category_for_file(self, file_path: str) -> str:
        """Suggest appropriate category for uncategorized file."""

        path_obj = Path(file_path)
        return self._determine_category(self.docs_root / path_obj)

    def execute_migration(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute the content migration."""

        print(f"🔄 {'DRY RUN: ' if dry_run else ''}Starting content migration...")

        migration_results = {
            "files_moved": 0,
            "files_skipped": 0,
            "errors": [],
            "new_structure": {},
            "dry_run": dry_run
        }

        analysis = self.analyze_current_structure()

        for target_category, files in analysis["migration_candidates"].items():
            target_dir = self.docs_root / target_category
            target_dir.mkdir(exist_ok=True)

            if target_category not in migration_results["new_structure"]:
                migration_results["new_structure"][target_category] = []

            for file_path in files:
                # Remove suggestion markers
                clean_path = file_path.replace(" (suggested)", "")

                source_file = self.docs_root / clean_path
                if not source_file.exists():
                    migration_results["errors"].append(f"Source file not found: {clean_path}")
                    continue

                # Determine target filename
                target_filename = self._generate_target_filename(clean_path, target_category)
                target_file = target_dir / target_filename

                if not dry_run:
                    try:
                        # Move the file
                        shutil.move(str(source_file), str(target_file))

                        # Update frontmatter category if needed
                        self._update_frontmatter_category(target_file, target_category)

                        migration_results["files_moved"] += 1
                        print(f"✅ Moved: {clean_path} → {target_category}/{target_filename}")

                    except Exception as e:
                        migration_results["errors"].append(f"Failed to move {clean_path}: {e}")
                        print(f"❌ Failed: {clean_path} - {e}")
                else:
                    print(f"📋 Would move: {clean_path} → {target_category}/{target_filename}")
                    migration_results["files_moved"] += 1

                migration_results["new_structure"][target_category].append(target_filename)

        print(f"{'📋 Dry run' if dry_run else '✅ Migration'} complete: {migration_results['files_moved']} files processed")
        return migration_results

    def _generate_target_filename(self, source_path: str, target_category: str) -> str:
        """Generate appropriate target filename."""

        source_name = Path(source_path).name

        # For getting started, add sequential numbering
        if target_category == "01-getting-started":
            base_name = source_name.replace('.md', '')

            # Define sequence for getting started
            sequence_map = {
                "overview": "01-overview.md",
                "quick-start": "02-quick-start.md",
                "first": "03-first-deployment.md",
                "troubleshoot": "04-troubleshooting.md",
                "beginner": "01-beginner-guide.md"
            }

            for keyword, target_name in sequence_map.items():
                if keyword in base_name.lower():
                    return target_name

            # Default to 01- if no specific match
            return f"01-{source_name}"

        # For other categories, keep original name but ensure it follows conventions
        return source_name

    def _update_frontmatter_category(self, file_path: Path, new_category: str):
        """Update the category in file frontmatter."""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        frontmatter["category"] = new_category.replace("01-", "").replace("02-", "").replace("03-", "").replace("04-", "").replace("05-", "").replace("06-", "")

                        # Write back updated frontmatter
                        updated_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
                        new_content = f"---\n{updated_frontmatter}---{parts[2]}"

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)

                    except yaml.YAMLError:
                        pass

        except Exception as e:
            print(f"⚠️ Failed to update frontmatter for {file_path}: {e}")

    def create_category_readmes(self):
        """Create README files for each new category."""

        category_descriptions = {
            "01-getting-started": {
                "title": "Getting Started",
                "description": "Sequential onboarding guides for new users",
                "audience": "New users, beginners, first-time setup",
                "content": [
                    "01-overview.md - Project overview and introduction",
                    "02-quick-start.md - 5-minute setup guide",
                    "03-first-deployment.md - Basic deployment instructions",
                    "04-troubleshooting.md - Common issues and solutions"
                ]
            },
            "02-development": {
                "title": "Development",
                "description": "Development workflows, setup, and processes",
                "audience": "Developers, contributors, technical team",
                "content": [
                    "Setup and installation guides",
                    "Development workflows",
                    "Testing procedures",
                    "Build and deployment processes",
                    "Debugging techniques"
                ]
            },
            "03-architecture": {
                "title": "Architecture",
                "description": "System design, architecture, and technical references",
                "audience": "Architects, technical leads, system designers",
                "content": [
                    "System architecture overviews",
                    "Component designs and patterns",
                    "Technical specifications",
                    "Integration guides",
                    "Infrastructure documentation"
                ]
            },
            "04-operations": {
                "title": "Operations",
                "description": "Operational procedures, monitoring, and maintenance",
                "audience": "Operators, DevOps engineers, system administrators",
                "content": [
                    "Runbooks and operational procedures",
                    "Monitoring and alerting guides",
                    "Maintenance procedures",
                    "Incident response guides",
                    "Performance optimization"
                ]
            },
            "05-governance": {
                "title": "Governance",
                "description": "Policies, standards, compliance, and governance",
                "audience": "Leaders, compliance officers, policy makers",
                "content": [
                    "Project policies and standards",
                    "Compliance requirements",
                    "Security guidelines",
                    "Governance procedures",
                    "Ownership and accountability"
                ]
            },
            "06-meta": {
                "title": "Documentation System",
                "description": "Documentation about the documentation system itself",
                "audience": "Documentation maintainers, automation engineers",
                "content": [
                    "System overview and architecture",
                    "Maintenance and contribution guides",
                    "Quality standards and validation",
                    "Automation tools and workflows",
                    "Search and indexing documentation"
                ]
            }
        }

        for category, info in category_descriptions.items():
            readme_path = self.docs_root / category / "README.md"

            readme_content = f"""---
status: active
last_updated: 2026-01-27
category: meta
---

# {info['title']}

{info['description']}

## Overview

**Audience:** {info['audience']}

This section contains documentation related to {info['description'].lower()}.

"""

            if 'content' in info:
                readme_content += "\n## Content\n\n"
                for item in info['content']:
                    readme_content += f"- {item}\n"

            readme_content += f"""
## Navigation

- [← Back to Main Documentation](../README.md)
- [📚 Documentation Portal](../index.html)

## Last Updated

2026-01-27 - Content migrated to new category structure

---
*This documentation follows the Xoe-NovAi documentation standards and organization framework.*
"""

            try:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                print(f"✅ Created README: {readme_path}")
            except Exception as e:
                print(f"❌ Failed to create README {readme_path}: {e}")

    def generate_migration_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive migration report."""

        report = []
        report.append("# 📋 Documentation Migration Report")
        report.append(f"**Date:** January 27, 2026")
        report.append(f"**Migration Type:** Category Restructuring")
        report.append("")

        # Summary
        report.append("## 📊 Summary")
        report.append(f"- **Files Processed:** {results.get('files_moved', 0)}")
        report.append(f"- **Categories Created:** {len(results.get('new_structure', {}))}")
        report.append(f"- **Errors:** {len(results.get('errors', []))}")
        report.append(f"- **Dry Run:** {'Yes' if results.get('dry_run', False) else 'No'}")
        report.append("")

        # New Structure
        if results.get('new_structure'):
            report.append("## 🗂️ New Category Structure")
            for category, files in results['new_structure'].items():
                report.append(f"### {category}")
                report.append(f"**Files:** {len(files)}")
                if len(files) <= 10:  # Show all if small number
                    for file in sorted(files):
                        report.append(f"- {file}")
                else:  # Show first few + count
                    for file in sorted(files)[:5]:
                        report.append(f"- {file}")
                    report.append(f"- ... and {len(files) - 5} more files")
                report.append("")

        # Errors
        if results.get('errors'):
            report.append("## ❌ Errors")
            for error in results['errors'][:10]:  # Limit to first 10
                report.append(f"- {error}")
            if len(results['errors']) > 10:
                report.append(f"- ... and {len(results['errors']) - 10} more errors")
            report.append("")

        # Next Steps
        report.append("## 🚀 Next Steps")
        report.append("1. **Review Migration:** Verify files are in correct categories")
        report.append("2. **Update Links:** Fix any broken internal references")
        report.append("3. **Update Navigation:** Refresh main documentation index")
        report.append("4. **Rebuild Index:** Run documentation indexer to update search")
        report.append("5. **Test Access:** Verify all documentation remains accessible")
        report.append("")

        return "\n".join(report)


def main():
    """Main migration execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Xoe-NovAi Documentation Migration Tool")
    parser.add_argument("--analyze", action="store_true", help="Analyze current structure only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without doing it")
    parser.add_argument("--execute", action="store_true", help="Execute the actual migration")
    parser.add_argument("--create-readmes", action="store_true", help="Create README files for new categories")

    args = parser.parse_args()

    docs_root = Path("docs/")
    migrator = ContentMigrator(docs_root)

    if args.analyze:
        print("🔍 Analyzing current documentation structure...")
        analysis = migrator.analyze_current_structure()

        print(f"📊 Found {analysis['total_files']} total files")
        print(f"📂 Categorized: {sum(len(files) for files in analysis['categories_found'].values())}")
        print(f"❓ Uncategorized: {len(analysis['uncategorized'])}")

        print("\n📋 Migration Plan:")
        for category, files in analysis['migration_candidates'].items():
            print(f"  {category}: {len(files)} files")

    elif args.dry_run:
        print("📋 Performing dry run migration...")
        results = migrator.execute_migration(dry_run=True)

        print(f"\n📋 Migration Report:")
        print(f"  Files to move: {results['files_moved']}")
        print(f"  Errors: {len(results['errors'])}")

    elif args.execute:
        print("⚠️  Executing actual migration...")
        confirm = input("This will move files to new category structure. Continue? (y/N): ")
        if confirm.lower() == 'y':
            results = migrator.execute_migration(dry_run=False)

            # Generate and save migration report
            report = migrator.generate_migration_report(results)
            report_path = docs_root / "migration-report.md"
            with open(report_path, 'w') as f:
                f.write(report)

            print(f"📋 Migration report saved to: {report_path}")
        else:
            print("Migration cancelled.")

    elif args.create_readmes:
        print("📝 Creating category README files...")
        migrator.create_category_readmes()

    else:
        print("Usage: python migrate_content.py [--analyze|--dry-run|--execute|--create-readmes]")


if __name__ == "__main__":
    main()
