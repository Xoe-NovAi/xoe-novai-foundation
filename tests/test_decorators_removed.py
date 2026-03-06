#!/usr/bin/env python3
"""
Simple test to verify that all decorators have been removed from the codebase.
This test doesn't require numpy or other complex dependencies.
"""

import ast
import os
import sys
from pathlib import Path


def find_python_files(directory):
    """Find all Python files in the given directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and other non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    return python_files


def check_for_decorators(file_path):
    """Check if a Python file contains any decorators."""
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
    """Main function to check for decorators in the codebase."""
    print("Checking for decorators in Python files...")
    
    # Find all Python files
    python_files = find_python_files('.')
    
    print(f"Found {len(python_files)} Python files to check")
    
    # Check each file for decorators
    all_decorators = []
    for file_path in python_files:
        decorators = check_for_decorators(file_path)
        all_decorators.extend(decorators)
    
    # Report results
    if all_decorators:
        print(f"\n❌ Found {len(all_decorators)} decorators in the codebase:")
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
        print("\n✅ No decorators found in the codebase!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)