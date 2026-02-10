#!/usr/bin/env python3
"""
Setup Podman secrets for Vikunja deployment.
Creates database password and JWT secret for rootless deployment.
"""

import subprocess
import sys
import os
import secrets
import string


def run_command(cmd, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def check_podman_secret_exists(secret_name):
    """Check if a Podman secret exists."""
    result = run_command(f"podman secret inspect {secret_name}", capture_output=True)
    return result is not None


def create_podman_secret(secret_name, secret_value):
    """Create a Podman secret."""
    print(f"Creating Podman secret: {secret_name}")
    
    # Use echo to pipe the secret value to podman secret create
    cmd = f"echo '{secret_value}' | podman secret create {secret_name} -"
    result = run_command(cmd, capture_output=False)
    
    if result is not None:
        print(f"✓ Successfully created secret: {secret_name}")
        return True
    else:
        print(f"✗ Failed to create secret: {secret_name}")
        return False


def generate_password(length=32):
    """Generate a secure password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret(length=64):
    """Generate a JWT secret."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def setup_secrets():
    """Setup all required secrets for Vikunja."""
    print("Setting up Podman secrets for Vikunja deployment...")
    
    # Generate secrets
    db_password = generate_password(32)
    jwt_secret = generate_jwt_secret(64)
    
    print(f"Generated secrets:")
    print(f"  DB Password: {db_password[:8]}... (truncated)")
    print(f"  JWT Secret: {jwt_secret[:8]}... (truncated)")
    print()
    
    # Check and create database password secret
    if not check_podman_secret_exists("db-pass"):
        if not create_podman_secret("db-pass", db_password):
            print("Failed to create db-pass secret. Exiting.")
            sys.exit(1)
    else:
        print("✓ db-pass secret already exists")
    
    # Check and create JWT secret
    if not check_podman_secret_exists("jwt-secret"):
        if not create_podman_secret("jwt-secret", jwt_secret):
            print("Failed to create jwt-secret. Exiting.")
            sys.exit(1)
    else:
        print("✓ jwt-secret secret already exists")
    
    print("\n✓ All Podman secrets have been set up successfully!")
    print("You can now deploy Vikunja with:")
    print("  podman-compose -f docker-compose.vikunja.yml up -d")


def cleanup_secrets():
    """Remove Podman secrets (for testing/cleanup)."""
    print("Cleaning up Podman secrets...")
    
    secrets_to_remove = ["db-pass", "jwt-secret"]
    
    for secret_name in secrets_to_remove:
        if check_podman_secret_exists(secret_name):
            result = run_command(f"podman secret rm {secret_name}", capture_output=False)
            if result is not None:
                print(f"✓ Removed secret: {secret_name}")
            else:
                print(f"✗ Failed to remove secret: {secret_name}")
        else:
            print(f"✓ Secret {secret_name} does not exist (skipping)")
    
    print("Cleanup complete.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Podman secrets for Vikunja')
    parser.add_argument('--cleanup', action='store_true', help='Remove existing secrets')
    
    args = parser.parse_args()
    
    # Check if Podman is available
    if run_command("podman --version") is None:
        print("Error: Podman is not installed or not available in PATH")
        sys.exit(1)
    
    # Check if user is in podman group or running as root
    if os.getuid() != 0 and 'podman' not in subprocess.getoutput('groups'):
        print("Warning: You may need to be in the podman group or use sudo for rootless Podman")
        print("Try: sudo usermod -aG podman $USER")
        print("Then log out and back in, or use: newgrp podman")
    
    if args.cleanup:
        cleanup_secrets()
    else:
        setup_secrets()


if __name__ == '__main__':
    main()