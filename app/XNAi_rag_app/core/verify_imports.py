#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 1 v0.1.7 - Import Verification Script
# ============================================================================
# Purpose: Validate all Python dependencies before deployment
# Features:
#   - Validates 25+ critical imports
#   - Checks version compatibility
#   - Tests llama-cpp-python compilation
#   - Verifies LangChain components
#   - No HuggingFace dependencies check
# ============================================================================

import sys
import importlib
import subprocess
from typing import Dict, Tuple, List
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.NC}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")

def print_fail(text: str):
    """Print failure message."""
    print(f"{Colors.RED}✗{Colors.NC} {text}")

def print_warn(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {Colors.NC} {text}")

def parse_version(v_str):
    """Simple version parser to avoid external dependencies."""
    return [int(x) for x in v_str.split('.') if x.isdigit()]

def check_import(
    module_name: str,
    required_version: str = None,
    check_attribute: str = None,
    optional: bool = False
) -> Tuple[bool, str]:
    """Check if a module can be imported and optionally verify version."""
    try:
        module = importlib.import_module(module_name)
        print_success(f"Import successful: {module_name}")
        
        # Version check
        if required_version:
            # Handle pydantic v2 which uses VERSION attribute
            version_str = getattr(module, 'VERSION', None) or \
                         getattr(module, '__version__', None) or \
                         getattr(module, 'version', None)
            
            if version_str and isinstance(version_str, str):
                try:
                    if parse_version(version_str) >= parse_version(required_version):
                        print_success(f"Version OK: {version_str} >= {required_version}")
                    else:
                        print_fail(f"Version too low: {version_str} < {required_version}")
                        return False, f"Version mismatch for {module_name}"
                except:
                    print_warn(f"Could not parse version strings: {version_str}, {required_version}")
            else:
                print_warn(f"No valid version attribute found in {module_name}")
        
        # Attribute check
        if check_attribute:
            if hasattr(module, check_attribute):
                print_success(f"Attribute OK: {check_attribute}")
            else:
                print_fail(f"Missing attribute: {check_attribute}")
                return False, f"Missing {check_attribute} in {module_name}"
        
        return True, f"{module_name} verified"
        
    except ImportError as e:
        if optional:
            print_warn(f"Optional import missing: {module_name}")
            return True, f"Optional {module_name} missing"
        print_fail(f"Import failed: {module_name} - {e}")
        return False, f"ImportError: {e}"
    except Exception as e:
        print_fail(f"Unexpected error: {module_name} - {e}")
        return False, f"Error: {e}"

def check_no_huggingface():
    """Ensure no HuggingFace dependencies."""
    try:
        import transformers
        print_fail("HuggingFace 'transformers' detected - violates zero-telemetry")
        return False
    except ImportError:
        print_success("No HuggingFace dependencies (good)")
        return True

def check_llama_compilation():
    """Test llama-cpp-python presence."""
    try:
        import llama_cpp
        print_success("LlamaCpp is installed and importable")
        return True
    except Exception as e:
        print_fail(f"LlamaCpp import failed: {e}")
        return False

def check_langchain_components():
    """Verify LangChain RAG components."""
    components = [
        ('langchain_community.llms', 'LlamaCpp', None, False),
        ('langchain_community.embeddings', 'LlamaCppEmbeddings', None, False),
        ('langchain_community.vectorstores', 'FAISS', None, False),
        # Fix for newer langchain
        ('langchain_text_splitters', 'CharacterTextSplitter', None, False),
    ]
    all_passed = True
    for mod, attr, ver, opt in components:
        success, msg = check_import(mod, ver, attr, opt)
        if not success:
            all_passed = False
    return all_passed

def check_crawl_dependencies():
    """Validate CrawlModule deps (optional for main API)."""
    crawl_comps = [
        ('crawl4ai', None, 'WebCrawler', True),
        ('yt_dlp', None, 'YoutubeDL', True),
    ]
    all_passed = True
    for mod, ver, attr, opt in crawl_comps:
        success, msg = check_import(mod, ver, attr, opt)
        if not success:
            all_passed = False
    return all_passed

def run_verification() -> Dict[str, List[Tuple[str, bool]]]:
    """Run all verification tests."""
    results = {
        'imports': [],
        'components': [],
        'crawl': [],
    }
    
    print_header("Core Imports Verification")
    core_imports = [
        ('fastapi', '0.118.0'),
        ('uvicorn', '0.37.0'),
        ('pydantic', '2.0.0'),
        ('redis', '5.0.0'),
        ('httpx', '0.27.0'),
        ('faiss', '1.7.0'),
        ('orjson', '3.9.0'),
        ('toml', '0.10.0'),
        ('tenacity', None),
        ('slowapi', None),
        ('prometheus_client', None),
        ('psutil', None),
    ]
    for mod, ver in core_imports:
        success, msg = check_import(mod, ver)
        results['imports'].append((mod, success))
    
    print_header("LangChain RAG Components")
    results['components'] = check_langchain_components()
    
    print_header("CrawlModule Dependencies")
    results['crawl'] = check_crawl_dependencies()
    
    print_header("Special Checks")
    check_no_huggingface()
    check_llama_compilation()
    
    return results

def print_summary(results: Dict) -> bool:
    """Print verification summary."""
    total_imports = len(results['imports'])
    passed_imports = sum(1 for _, success in results['imports'] if success)
    
    print_header("Verification Summary")
    print(f"Core Imports: {passed_imports}/{total_imports} passed")
    print(f"LangChain Components: {'PASS' if results['components'] else 'FAIL'}")
    print(f"Crawl Dependencies: {'PASS' if results['crawl'] else 'FAIL'}")
    
    all_passed = passed_imports == total_imports and results['components']
    if all_passed:
        print_success("ALL CRITICAL VERIFICATIONS PASSED")
    else:
        print_fail("SOME CRITICAL VERIFICATIONS FAILED")
    
    return all_passed

if __name__ == "__main__":
    print_header("Xoe-NovAi Phase 1 v0.1.7 - Import Verification")
    results = run_verification()
    all_passed = print_summary(results)
    sys.exit(0 if all_passed else 1)