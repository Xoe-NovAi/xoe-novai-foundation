#!/usr/bin/env python3
"""
Phase Organization Validation Script
Validates the complete reorganization and ensures all links work.
"""

import os
import re
from pathlib import Path
import requests
from urllib.parse import urlparse

def validate_organization():
    """Main validation function."""
    print("🔍 Starting Phase Organization Validation...")
    
    base_path = Path("internal_docs/01-strategic-planning")
    
    # Validate directory structure
    validate_directory_structure(base_path)
    
    # Validate document links
    validate_document_links(base_path)
    
    # Validate naming conventions
    validate_naming_conventions(base_path)
    
    # Validate agent accessibility
    validate_agent_accessibility(base_path)
    
    print("✅ Validation complete!")

def validate_directory_structure(base_path):
    """Validate that all required directories exist."""
    print("📁 Validating directory structure...")
    
    required_dirs = [
        "phases",
        "PHASE-EXECUTION-INDEXES",
        "research-phases"
    ]
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            print(f"❌ Missing directory: {dir_path}")
        else:
            print(f"✅ Directory exists: {dir_path}")
    
    # Validate phase directories
    for phase_num in range(0, 17):
        phase_dir = base_path / "phases" / f"PHASE-{phase_num}"
        required_subdirs = ["resources", "progress", "ai-generated-insights", "faiss-index"]
        
        for subdir in required_subdirs:
            if not (phase_dir / subdir).exists():
                print(f"❌ Missing subdirectory: {phase_dir / subdir}")
            else:
                print(f"✅ Subdirectory exists: {phase_dir / subdir}")

def validate_document_links(base_path):
    """Validate that all document links are functional."""
    print("🔗 Validating document links...")
    
    markdown_files = list(base_path.rglob("*.md"))
    broken_links = []
    
    for md_file in markdown_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all markdown links
        links = re.findall(r'\[.*?\]\((.*?)\)', content)
        
        for link in links:
            if link.startswith('http'):
                continue  # Skip external links
            
            # Convert relative link to absolute path
            link_path = (md_file.parent / link).resolve()
            
            if not link_path.exists():
                broken_links.append({
                    'file': str(md_file),
                    'link': link,
                    'target': str(link_path)
                })
    
    if broken_links:
        print(f"❌ Found {len(broken_links)} broken links:")
        for link_info in broken_links[:10]:  # Show first 10
            print(f"   {link_info['file']} → {link_info['link']}")
        if len(broken_links) > 10:
            print(f"   ... and {len(broken_links) - 10} more")
    else:
        print("✅ All document links are functional")

def validate_naming_conventions(base_path):
    """Validate that documents follow naming conventions."""
    print("📝 Validating naming conventions...")
    
    phase_files = list((base_path / "phases").rglob("*.md"))
    naming_issues = []
    
    for file_path in phase_files:
        filename = file_path.name
        
        # Check for proper phase prefix
        if not re.match(r'PHASE-\d+', filename) and not filename.startswith('00-README'):
            naming_issues.append(f"Improper naming: {file_path}")
    
    if naming_issues:
        print(f"❌ Found {len(naming_issues)} naming convention issues:")
        for issue in naming_issues[:5]:  # Show first 5
            print(f"   {issue}")
        if len(naming_issues) > 5:
            print(f"   ... and {len(naming_issues) - 5} more")
    else:
        print("✅ All documents follow naming conventions")

def validate_agent_accessibility(base_path):
    """Validate that AI agents can easily access documents."""
    print("🤖 Validating agent accessibility...")
    
    # Check for README files in each phase
    missing_readmes = []
    for phase_num in range(0, 17):
        readme_path = base_path / "phases" / f"PHASE-{phase_num}" / f"00-README-PHASE-{phase_num}.md"
        if not readme_path.exists():
            missing_readmes.append(f"PHASE-{phase_num}")
    
    if missing_readmes:
        print(f"❌ Missing README files for phases: {', '.join(missing_readmes)}")
    else:
        print("✅ All phases have README files")
    
    # Check for master index
    master_index = base_path / "PHASE-EXECUTION-INDEXES" / "00-MASTER-NAVIGATION-INDEX.md"
    if not master_index.exists():
        print("❌ Missing master navigation index")
    else:
        print("✅ Master navigation index exists")
    
    # Check for phase indexes
    missing_indexes = []
    for phase_num in range(0, 17):
        index_path = base_path / "PHASE-EXECUTION-INDEXES" / f"{phase_num:02d}-PHASE-{phase_num}-INDEX.md"
        if not index_path.exists():
            missing_indexes.append(f"PHASE-{phase_num}")
    
    if missing_indexes:
        print(f"❌ Missing phase indexes for: {', '.join(missing_indexes)}")
    else:
        print("✅ All phase indexes exist")

if __name__ == "__main__":
    validate_organization()