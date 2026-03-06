#!/usr/bin/env python3
"""
Diataxis Organization Validation Script
Validates the complete Diataxis-enhanced phase organization implementation.
"""

import os
import json
from pathlib import Path
import subprocess

def validate_diataxis_structure():
    """Validate the complete Diataxis structure."""
    base_path = Path("internal_docs/01-strategic-planning")
    
    print("🔍 Validating Diataxis Structure...")
    
    # Check main directories
    required_dirs = [
        "phases",
        "PHASE-EXECUTION-INDEXES",
        "session-state-organization"
    ]
    
    for directory in required_dirs:
        dir_path = base_path / directory
        if dir_path.exists():
            print(f"✅ {directory} directory exists")
        else:
            print(f"❌ {directory} directory missing")
            return False
    
    # Check phase directories
    for phase_num in range(0, 17):
        phase_dir = base_path / "phases" / f"PHASE-{phase_num}"
        
        # Check Diataxis categories
        diataxis_categories = [
            "🚀 TUTORIALS",
            "🛠️ HOW-TO-GUIDES", 
            "📖 REFERENCE",
            "🧠 EXPLANATION"
        ]
        
        for category in diataxis_categories:
            category_dir = phase_dir / category
            if category_dir.exists():
                print(f"✅ Phase {phase_num} - {category} exists")
            else:
                print(f"❌ Phase {phase_num} - {category} missing")
                return False
        
        # Check standard subdirectories
        subdirs = ["resources", "progress", "ai-generated-insights", "faiss-index"]
        for subdir in subdirs:
            subdir_path = phase_dir / subdir
            if subdir_path.exists():
                print(f"✅ Phase {phase_num} - {subdir} exists")
            else:
                print(f"❌ Phase {phase_num} - {subdir} missing")
                return False
        
        # Check README
        readme_path = phase_dir / f"00-README-PHASE-{phase_num}.md"
        if readme_path.exists():
            print(f"✅ Phase {phase_num} - README exists")
        else:
            print(f"❌ Phase {phase_num} - README missing")
            return False
    
    print("✅ All phase directories validated successfully!")
    return True

def validate_index_files():
    """Validate index files."""
    base_path = Path("internal_docs/01-strategic-planning")
    
    print("🔍 Validating Index Files...")
    
    # Check master index
    master_index = base_path / "PHASE-EXECUTION-INDEXES" / "00-MASTER-NAVIGATION-INDEX.md"
    if master_index.exists():
        print("✅ Master navigation index exists")
    else:
        print("❌ Master navigation index missing")
        return False
    
    # Check phase indexes
    for phase_num in range(0, 17):
        phase_index = base_path / "PHASE-EXECUTION-INDEXES" / f"{phase_num:02d}-PHASE-{phase_num}-INDEX.md"
        if phase_index.exists():
            print(f"✅ Phase {phase_num} index exists")
        else:
            print(f"❌ Phase {phase_num} index missing")
            return False
    
    print("✅ All index files validated successfully!")
    return True

def validate_session_state_organization():
    """Validate session-state organization."""
    base_path = Path("internal_docs/01-strategic-planning")
    
    print("🔍 Validating Session-State Organization...")
    
    session_org_dir = base_path / "session-state-organization"
    
    # Check session-state organization structure
    required_subdirs = ["mappings", "migrated", "archive"]
    for subdir in required_subdirs:
        subdir_path = session_org_dir / subdir
        if subdir_path.exists():
            print(f"✅ Session-state {subdir} directory exists")
        else:
            print(f"❌ Session-state {subdir} directory missing")
            return False
    
    # Check mapping file
    mapping_file = session_org_dir / "MAPPING.md"
    if mapping_file.exists():
        print("✅ Session-state mapping file exists")
    else:
        print("❌ Session-state mapping file missing")
        return False
    
    print("✅ Session-state organization validated successfully!")
    return True

def validate_mkdocs_integration():
    """Validate MkDocs integration."""
    print("🔍 Validating MkDocs Integration...")
    
    # Check public MkDocs configuration
    public_mkdocs = Path("mkdocs.yml")
    if public_mkdocs.exists():
        print("✅ Public MkDocs configuration exists")
    else:
        print("❌ Public MkDocs configuration missing")
        return False
    
    # Check internal MkDocs configuration
    internal_mkdocs = Path("mkdocs-internal.yml")
    if internal_mkdocs.exists():
        print("✅ Internal MkDocs configuration exists")
    else:
        print("❌ Internal MkDocs configuration missing")
        return False
    
    # Check integration documentation
    integration_doc = Path("internal_docs/01-strategic-planning/PHASE-ORGANIZATION-MKDOCS-INTEGRATION.md")
    if integration_doc.exists():
        print("✅ MkDocs integration documentation exists")
    else:
        print("❌ MkDocs integration documentation missing")
        return False
    
    print("✅ MkDocs integration validated successfully!")
    return True

def validate_diataxis_content():
    """Validate Diataxis content classification."""
    base_path = Path("internal_docs/01-strategic-planning")
    
    print("🔍 Validating Diataxis Content...")
    
    # Check for content in each Diataxis category
    diataxis_categories = [
        "🚀 TUTORIALS",
        "🛠️ HOW-TO-GUIDES", 
        "📖 REFERENCE",
        "🧠 EXPLANATION"
    ]
    
    for phase_num in range(0, 17):
        phase_dir = base_path / "phases" / f"PHASE-{phase_num}"
        
        for category in diataxis_categories:
            category_dir = phase_dir / category
            
            # Check for content files
            content_files = list(category_dir.glob("*.md"))
            if content_files:
                print(f"✅ Phase {phase_num} - {category} has content")
            else:
                print(f"⚠️  Phase {phase_num} - {category} is empty (expected for planning phases)")
    
    print("✅ Diataxis content validation completed!")
    return True

def validate_agent_optimization():
    """Validate agent optimization features."""
    print("🔍 Validating Agent Optimization...")
    
    # Check agent guide
    agent_guide = Path("expert-knowledge/agent-tooling/PHASE-ORGANIZATION-AGENT-GUIDE.md")
    if agent_guide.exists():
        print("✅ Agent guide exists")
    else:
        print("❌ Agent guide missing")
        return False
    
    # Check Diataxis enhanced plan
    diataxis_plan = Path("internal_docs/01-strategic-planning/PHASE-ORGANIZATION-DIATACTICS-ENHANCED.md")
    if diataxis_plan.exists():
        print("✅ Diataxis enhanced plan exists")
    else:
        print("❌ Diataxis enhanced plan missing")
        return False
    
    print("✅ Agent optimization validated successfully!")
    return True

def generate_validation_report():
    """Generate a comprehensive validation report."""
    report = {
        "validation_date": "2026-02-17",
        "organization_type": "Diataxis-Enhanced Phase Organization",
        "total_phases": 17,
        "diataxis_categories": 4,
        "validation_results": {
            "structure": validate_diataxis_structure(),
            "indexes": validate_index_files(),
            "session_state": validate_session_state_organization(),
            "mkdocs_integration": validate_mkdocs_integration(),
            "content_classification": validate_diataxis_content(),
            "agent_optimization": validate_agent_optimization()
        }
    }
    
    # Calculate overall status
    all_valid = all(report["validation_results"].values())
    report["overall_status"] = "PASS" if all_valid else "FAIL"
    
    # Save report
    report_path = Path("internal_docs/01-strategic-planning/PHASE-EXECUTION-INDEXES/validation-report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    """Main validation function."""
    print("🚀 Starting Diataxis Organization Validation...")
    print("=" * 60)
    
    # Run all validations
    report = generate_validation_report()
    
    # Print summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    for category, result in report["validation_results"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{category.upper()}: {status}")
    
    print(f"\n🎯 OVERALL STATUS: {report['overall_status']}")
    
    if report["overall_status"] == "PASS":
        print("\n🎉 All validations passed! Diataxis organization is complete and ready.")
    else:
        print("\n⚠️  Some validations failed. Please review the issues above.")
    
    print(f"\n📄 Detailed report saved to: {report['validation_date']}/validation-report.json")
    
    return report["overall_status"] == "PASS"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)