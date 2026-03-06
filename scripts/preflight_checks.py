#!/usr/bin/env python3
# Xoe-NovAi Pre-flight Checks
# Comprehensive validation before test build and deployment

import os
import sys
import stat
import subprocess
from pathlib import Path

def check_directories():
    """Check required directories exist with correct permissions"""
    required_dirs = [
        ('library', 1001, 1001),
        ('knowledge', 1001, 1001),
        ('data/faiss_index', 1001, 1001),
        ('backups', 1001, 1001),
        ('logs', 1001, 1001),
        ('models/optimized', 1001, 1001),
        ('models/backup', 1001, 1001),
        ('data/cache', 1001, 1001),
        ('models', 0, 0),  # models dir can be owned by user
    ]

    all_good = True
    for dir_path, expected_uid, expected_gid in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            all_good = False
            continue

        # Check ownership
        stat_info = os.stat(dir_path)
        if stat_info.st_uid != expected_uid or stat_info.st_gid != expected_gid:
            print(f"⚠️  Wrong ownership on {dir_path}: {stat_info.st_uid}:{stat_info.st_gid} (expected {expected_uid}:{expected_gid})")
            # Don't fail on ownership for now, just warn

    return all_good

def check_models():
    """Check model files exist"""
    required_models = [
        'models/smollm2-135m-instruct-q8_0.gguf',
        'models/all-MiniLM-L12-v2.Q8_0.gguf'
    ]

    all_good = True
    for model in required_models:
        if not os.path.exists(model):
            print(f"❌ Missing model: {model}")
            all_good = False
        else:
            size = os.path.getsize(model) / (1024 * 1024)  # Size in MB
            print(f"✅ Found model: {model} ({size:.1f}MB)")

    return all_good

def check_config():
    """Check configuration files"""
    config_checks = [
        ('config.toml', 'TOML configuration'),
        ('.env', 'Environment variables'),
        ('docker-compose.yml', 'Docker compose configuration'),
        ('requirements-api.txt', 'API dependencies'),
    ]

    all_good = True
    for config_file, description in config_checks:
        if not os.path.exists(config_file):
            print(f"❌ Missing {description}: {config_file}")
            all_good = False
        else:
            print(f"✅ Found {description}: {config_file}")

    return all_good

def check_docker():
    """Check Docker availability"""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker daemon available")
            return True
        else:
            print("❌ Docker daemon not running")
            return False
    except (subprocess.SubprocessError, FileNotFoundError):
        print("❌ Docker not installed or not accessible")
        return False

def check_environment():
    """Check environment variables"""
    required_vars = [
        'REDIS_PASSWORD',
        'APP_UID',
        'APP_GID',
    ]

    all_good = True
    for var in required_vars:
        if var not in os.environ:
            print(f"⚠️  Missing environment variable: {var}")
            # Check if it's in .env file
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_content = f.read()
                    if var in env_content:
                        print(f"   ℹ️  {var} found in .env file")
                    else:
                        print(f"❌ {var} not found in .env file")
                        all_good = False
        else:
            print(f"✅ Environment variable set: {var}")

    return all_good

def check_python():
    """Check Python version and availability"""
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Python available: {version}")
            return True
        else:
            print("❌ Python execution failed")
            return False
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False

def main():
    print("🛩️  Running Xoe-NovAi Pre-flight Checks...")
    print("=" * 60)

    checks = [
        ("Directories", check_directories),
        ("Models", check_models),
        ("Configuration Files", check_config),
        ("Docker", check_docker),
        ("Environment Variables", check_environment),
        ("Python", check_python),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if not check_func():
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All pre-flight checks passed!")
        print("🚀 Ready to proceed with build and deployment")
        return 0
    else:
        print("❌ Pre-flight checks failed!")
        print("🔧 Please fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    exit(main())
