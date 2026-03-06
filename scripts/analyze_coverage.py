#!/usr/bin/env python3
"""
Documentation Coverage Analyzer
==============================

Analyzes the coverage of codebase modules by documentation files.
Identifies undocumented services, core modules, and MCP servers.
"""

import os
from pathlib import Path
import argparse

# Key areas to check for coverage
CODE_AREAS = [
    "app/XNAi_rag_app/core",
    "app/XNAi_rag_app/services",
    "app/XNAi_rag_app/api",
    "app/XNAi_rag_app/workers",
    "mcp-servers"
]

# Documentation directories to search
DOC_DIRS = [
    "docs",
    "expert-knowledge"
]

def analyze_coverage(root_dir: str):
    """Analyze documentation coverage for key code areas."""
    root = Path(root_dir)
    report = {
        "areas": {},
        "total_modules": 0,
        "documented_modules": 0
    }
    
    # Get all documentation text for keyword searching
    all_doc_content = ""
    for doc_dir in DOC_DIRS:
        doc_path = root / doc_dir
        if doc_path.exists():
            for file_path in doc_path.rglob("*.md"):
                try:
                    all_doc_content += file_path.read_text(encoding='utf-8').lower() + " "
                except:
                    pass

    for area in CODE_AREAS:
        area_path = root / area
        if not area_path.exists():
            continue
            
        area_report = {
            "modules": [],
            "coverage_pct": 0,
            "total": 0,
            "documented": 0
        }
        
        # Look for python files or directories with __init__.py
        modules = []
        for item in area_path.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                modules.append(item.stem)
            elif item.is_dir() and (item / "__init__.py").exists():
                modules.append(item.name)
            elif area == "mcp-servers" and item.is_dir():
                modules.append(item.name)
                
        area_report["total"] = len(modules)
        report["total_modules"] += len(modules)
        
        documented_count = 0
        for module in modules:
            is_documented = module.lower() in all_doc_content
            if is_documented:
                documented_count += 1
            
            area_report["modules"].append({
                "name": module,
                "documented": is_documented
            })
            
        area_report["documented"] = documented_count
        if area_report["total"] > 0:
            area_report["coverage_pct"] = (documented_count / area_report["total"]) * 100
            
        report["areas"][area] = area_report
        report["documented_modules"] += documented_count
        
    if report["total_modules"] > 0:
        report["total_coverage_pct"] = (report["documented_modules"] / report["total_modules"]) * 100
    else:
        report["total_coverage_pct"] = 0
        
    return report

def generate_report(report: dict, output_path: str):
    """Generate markdown coverage report."""
    with open(output_path, "w") as f:
        f.write("# 📊 Documentation Coverage Report\n\n")
        f.write(f"**Total Coverage**: {report['total_coverage_pct']:.1f}%\n")
        f.write(f"**Modules Analyzed**: {report['total_modules']}\n")
        f.write(f"**Documented Modules**: {report['documented_modules']}\n\n")
        
        for area, data in report["areas"].items():
            f.write(f"## 📁 Area: {area}\n")
            f.write(f"**Coverage**: {data['coverage_pct']:.1f}% ({data['documented']}/{data['total']})\n\n")
            
            f.write("| Module | Status |\n")
            f.write("|--------|--------|\n")
            for mod in sorted(data["modules"], key=lambda x: x['name']):
                status = "✅ Documented" if mod["documented"] else "❌ Missing"
                f.write(f"| `{mod['name']}` | {status} |\n")
            f.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze documentation coverage.")
    parser.add_argument("--output", type=str, default="reports/doc-coverage.md", help="Output report path")
    args = parser.parse_args()
    
    project_root = os.getcwd()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print("Analyzing documentation coverage...")
    coverage_report = analyze_coverage(project_root)
    
    generate_report(coverage_report, args.output)
    print(f"Report generated: {args.output}")
