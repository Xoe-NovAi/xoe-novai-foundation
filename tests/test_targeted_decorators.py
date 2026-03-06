#!/usr/bin/env python3
"""
Targeted test to verify that decorators have been removed from specific files.
This test focuses on the files we've been working with.
"""

import ast
import os


def check_file_for_decorators(file_path):
    """Check if a specific Python file contains any decorators."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Find all function and class definitions
        decorators_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.decorator_list:
                    for decorator in node.decorator_list:
                        # Get decorator name
                        if isinstance(decorator, ast.Name):
                            decorator_name = decorator.id
                        elif isinstance(decorator, ast.Attribute):
                            decorator_name = decorator.attr
                        elif isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Name):
                                decorator_name = decorator.func.id
                            elif isinstance(decorator.func, ast.Attribute):
                                decorator_name = decorator.func.attr
                            else:
                                decorator_name = "unknown"
                        else:
                            decorator_name = "unknown"
                        
                        decorators_found.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': type(node).__name__,
                            'name': node.name,
                            'decorator': decorator_name
                        })
        
        return decorators_found
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def main():
    """Main function to check specific files for decorators."""
    print("Checking specific files for decorators...")
    
    # Files we've been working with
    target_files = [
        'app/XNAi_rag_app/api/healthcheck.py',
        'tests/test_vector_cache.py',
        'tests/test_decorators_removed.py',
        'tests/test_targeted_decorators.py'
    ]
    
    all_decorators = []
    for file_path in target_files:
        print(f"Checking {file_path}...")
        decorators = check_file_for_decorators(file_path)
        all_decorators.extend(decorators)
    
    # Report results
    if all_decorators:
        print(f"\n❌ Found {len(all_decorators)} decorators:")
        for decorator in all_decorators:
            print(f"  - {decorator['file']}:{decorator['line']} - {decorator['type']} {decorator['name']} - @{decorator['decorator']}")
        
        # Check for specific problematic decorators
        problematic_decorators = ['async', 'asyncio', 'pytest', 'unittest']
        problematic_found = [d for d in all_decorators if any(p in d['decorator'].lower() for p in problematic_decorators)]
        
        if problematic_found:
            print(f"\n⚠️  Found {len(problematic_found)} potentially problematic decorators:")
            for decorator in problematic_found:
                print(f"  - {decorator['file']}:{decorator['line']} - {decorator['decorator']}")
        
        return False
    else:
        print("\n✅ No decorators found in target files!")
        return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)