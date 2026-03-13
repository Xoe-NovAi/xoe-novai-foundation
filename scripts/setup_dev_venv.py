#!/usr/bin/env python3
"""
Development Environment Setup Script
Creates a Python 3.12 virtual environment for testing Vikunja integration
outside of Podman containers.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def check_python_version():
    """Check if Python 3.12+ is available"""
    if sys.version_info[:2] < (3, 12):
        print(f"❌ Python 3.12+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    elif sys.version_info[:2] == (3, 12):
        print(f"✅ Python 3.12 detected")
    else:
        print(f"⚠️  Python 3.12+ recommended, found {sys.version_info.major}.{sys.version_info.minor}")
    return True

def create_venv(venv_path):
    """Create virtual environment"""
    print(f"🔨 Creating virtual environment at {venv_path}")
    venv.create(venv_path, with_pip=True, upgrade_deps=True)
    return venv_path

def install_dependencies(venv_path):
    """Install required dependencies in virtual environment"""
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

    print(f"📦 Installing dependencies using {pip_path}")

    # Install requirements
    requirements_files = [
        "requirements-vikunja.txt",
        "requirements-api.txt",
        "requirements-chainlit.txt"
    ]

    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"📋 Installing from {req_file}")
            subprocess.run([str(python_path), "-m", "pip", "install", "-r", req_file], check=True)
        else:
            print(f"⚠️  Requirements file {req_file} not found, skipping")

    # Install additional development tools
    dev_packages = [
        "pytest",
        "pytest-asyncio",
        "black",
        "ruff",
        "mypy"
    ]

    print("🔧 Installing development tools")
    subprocess.run([str(python_path), "-m", "pip", "install"] + dev_packages, check=True)

    return python_path

def create_activation_script(venv_path):
    """Create activation script for easy use"""
    if sys.platform == "win32":
        script_content = f"""@echo off
echo Activating Vikunja development environment...
call {venv_path}\\Scripts\\activate.bat
echo.
echo Available commands:
echo   python scripts/memory_bank_export.py --dry-run
echo   python scripts/vikunja_importer.py vikunja-import.json --dry-run
echo   python scripts/deploy_vikunja_secure.py --help
echo.
echo To deactivate, run: deactivate
"""
        script_path = Path("activate_dev_env.bat")
    else:
        script_content = f"""#!/bin/bash
echo "Activating Vikunja development environment..."
source {venv_path}/bin/activate
echo ""
echo "Available commands:"
echo "  python scripts/memory_bank_export.py --dry-run"
echo "  python scripts/vikunja_importer.py vikunja-import.json --dry-run"
echo "  python scripts/deploy_vikunja_secure.py --help"
echo ""
echo "To deactivate, run: deactivate"
"""
        script_path = Path("activate_dev_env.sh")
        script_path.chmod(0o755)

    with open(script_path, "w") as f:
        f.write(script_content)

    print(f"✅ Created activation script: {script_path}")

def test_imports(python_path):
    """Test that all required imports work"""
    print("🧪 Testing imports...")

    test_imports = [
        "aiohttp",
        "tenacity",
        "python_frontmatter",
        "uvicorn",
        "chainlit"
    ]

    for module in test_imports:
        try:
            result = subprocess.run(
                [str(python_path), "-c", f"import {module}; print('✅ {module}')"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"❌ {module}: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {module}: {e}")

def main():
    """Main setup function"""
    print("🚀 Xoe-NovAi Vikunja Development Environment Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        print("❌ Python 3.12 is required for development")
        print("Please install Python 3.12 and try again")
        sys.exit(1)

    # Create venv directory
    venv_path = Path(".venv-vikunja")
    if venv_path.exists():
        print(f"⚠️  Virtual environment {venv_path} already exists")
        response = input("Remove existing environment? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Setup cancelled")
            sys.exit(1)
        import shutil
        shutil.rmtree(venv_path)

    # Create virtual environment
    create_venv(venv_path)

    # Install dependencies
    python_path = install_dependencies(venv_path)

    # Create activation script
    create_activation_script(venv_path)

    # Test imports
    test_imports(python_path)

    print("\n✅ Development environment setup complete!")
    print(f"Virtual environment: {venv_path}")
    print(f"Python executable: {python_path}")

    if sys.platform == "win32":
        print("\nTo activate the environment, run:")
        print("  activate_dev_env.bat")
    else:
        print("\nTo activate the environment, run:")
        print("  source activate_dev_env.sh")

    print("\nTo test the Vikunja integration:")
    print("  python scripts/memory_bank_export.py --dry-run")
    print("  python scripts/vikunja_importer.py vikunja-import.json --dry-run")

if __name__ == "__main__":
    main()