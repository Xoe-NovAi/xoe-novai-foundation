#!/usr/bin/env python3
"""
Secure Vikunja Deployment Script
Complete setup with rootless Podman, security hardening, and automated deployment.
"""

import subprocess
import sys
import os
import argparse
import time
from pathlib import Path


def run_command(cmd, capture_output=True, shell=True, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=shell, 
            capture_output=capture_output, 
            text=True, 
            check=check
        )
        return result.stdout.strip() if capture_output else True
    except subprocess.CalledProcessError as e:
        if capture_output:
            print(f"Error running command: {cmd}")
            print(f"Error: {e.stderr}")
        return None


def check_podman_available():
    """Check if Podman is available and properly configured."""
    print("Checking Podman availability...")
    
    # Check if Podman is installed
    if run_command("podman --version") is None:
        print("✗ Error: Podman is not installed or not available in PATH")
        return False
    
    # Check if user can run Podman commands
    if run_command("podman info", capture_output=True) is None:
        print("✗ Error: Cannot run Podman commands. Check permissions and configuration.")
        return False
    
    print("✓ Podman is available and configured")
    return True


def setup_permissions():
    """Setup proper permissions for rootless containers."""
    print("Setting up permissions for rootless containers...")
    
    # Ensure db and files directories exist with proper permissions
    directories = ["./db", "./files"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Set permissions for rootless containers
        result = run_command(f"podman unshare chown 1000:1000 -R {directory}", capture_output=False, check=False)
        if result is None:
            print(f"Warning: Could not set permissions for {directory}")
        else:
            print(f"✓ Set permissions for {directory}")
    
    return True


def setup_secrets():
    """Setup Podman secrets for Vikunja."""
    print("Setting up Podman secrets...")
    
    # Check if secrets already exist
    secrets_exist = True
    for secret in ["db-pass", "jwt-secret"]:
        if run_command(f"podman secret inspect {secret}", capture_output=True, check=False) is None:
            secrets_exist = False
            break
    
    if secrets_exist:
        print("✓ Podman secrets already exist")
        return True
    
    # Create secrets using the setup script
    setup_script = Path("scripts/setup_vikunja_secrets.py")
    if not setup_script.exists():
        print("✗ Error: setup_vikunja_secrets.py not found")
        return False
    
    result = run_command(f"python3 {setup_script}", capture_output=False)
    if result is None:
        print("✗ Failed to setup Podman secrets")
        return False
    
    print("✓ Podman secrets created successfully")
    return True


def prune_existing_resources():
    """Prune existing Vikunja-related resources for clean deployment."""
    print("Pruning existing Vikunja resources...")
    
    # Stop and remove existing containers
    run_command("podman ps -a -q --filter 'label=io.vikunja.project' | xargs -r podman rm -f", 
                capture_output=False, check=False)
    
    # Remove existing networks
    run_command("podman network ls -q --filter 'label=io.vikunja.project' | xargs -r podman network rm", 
                capture_output=False, check=False)
    
    # Remove existing volumes
    run_command("podman volume ls -q --filter 'label=io.vikunja.project' | xargs -r podman volume rm", 
                capture_output=False, check=False)
    
    print("✓ Existing Vikunja resources pruned")


def deploy_vikunja():
    """Deploy Vikunja using the hardened docker-compose file."""
    print("Deploying Vikunja with security hardening...")
    
    compose_file = "docker-compose.vikunja.yml"
    if not Path(compose_file).exists():
        print(f"✗ Error: {compose_file} not found")
        return False
    
    # Deploy with user namespace for rootless containers
    cmd = f"podman-compose -f {compose_file} up -d --userns=keep-id"
    result = run_command(cmd, capture_output=False)
    
    if result is None:
        print("✗ Failed to deploy Vikunja")
        return False
    
    print("✓ Vikunja deployment initiated")
    return True


def wait_for_health():
    """Wait for Vikunja services to be healthy."""
    print("Waiting for Vikunja services to become healthy...")
    
    max_wait = 300  # 5 minutes
    check_interval = 5
    elapsed = 0
    
    while elapsed < max_wait:
        # Check API health
        api_health = run_command("curl -sSf http://localhost:3456/api/v1/info", 
                                capture_output=True, check=False)
        
        # Check frontend health
        frontend_health = run_command("curl -sSf http://localhost:3456/", 
                                     capture_output=True, check=False)
        
        if api_health is not None and frontend_health is not None:
            print("✓ Vikunja services are healthy")
            return True
        
        print(f"  Waiting... ({elapsed}s/{max_wait}s)")
        time.sleep(check_interval)
        elapsed += check_interval
    
    print("✗ Timeout waiting for Vikunja services to become healthy")
    return False


def run_security_scan():
    """Run Trinity security scan on the deployed containers."""
    print("Running security scan on Vikunja containers...")
    
    # Get container IDs
    container_ids = run_command("podman ps -q --filter 'label=io.vikunja.project'", 
                               capture_output=True)
    
    if not container_ids:
        print("Warning: No Vikunja containers found for security scan")
        return True
    
    containers = container_ids.split()
    
    for container_id in containers:
        print(f"  Scanning container: {container_id[:12]}")
        
        # Export container for scanning
        tar_file = f"/tmp/{container_id[:12]}.tar"
        export_cmd = f"podman save -o {tar_file} {container_id}"
        if run_command(export_cmd, capture_output=False) is None:
            print(f"    Warning: Could not export container {container_id[:12]}")
            continue
        
        # Run Trivy scan
        scan_cmd = f"trivy image --input {tar_file} --format json --output /tmp/{container_id[:12]}-scan.json"
        if run_command(scan_cmd, capture_output=False, check=False) is None:
            print(f"    Warning: Trivy scan failed for {container_id[:12]}")
        
        # Clean up
        os.remove(tar_file)
    
    print("✓ Security scan completed")
    return True


def display_summary():
    """Display deployment summary and next steps."""
    print("\n" + "="*60)
    print("VIKUNJA DEPLOYMENT COMPLETE")
    print("="*60)
    print()
    print("Access Information:")
    print("  UI: http://localhost:3456")
    print("  API: http://localhost:3456/api/v1")
    print()
    print("Next Steps:")
    print("1. Access the UI to create your admin account")
    print("2. Get your API token from Settings > API")
    print("3. Export memory_bank tasks:")
    print("   python3 scripts/memory_bank_export.py --dry-run")
    print("4. Import tasks to Vikunja:")
    print("   python3 scripts/vikunja_importer.py vikunja-import.json --token YOUR_TOKEN")
    print()
    print("Security Notes:")
    print("  - All containers run as non-root user (UID 1000)")
    print("  - No new privileges allowed (--no-new-privileges)")
    print("  - SELinux labels applied (:Z,U)")
    print("  - Secrets managed via Podman secrets")
    print("  - Local-only access (no external exposure)")
    print()
    print("Management Commands:")
    print("  View logs: podman-compose -f docker-compose.vikunja.yml logs")
    print("  Stop: podman-compose -f docker-compose.vikunja.yml down")
    print("  Restart: podman-compose -f docker-compose.vikunja.yml restart")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Deploy Vikunja with security hardening')
    parser.add_argument('--cleanup', action='store_true', help='Clean up existing deployment')
    parser.add_argument('--skip-scan', action='store_true', help='Skip security scan')
    
    args = parser.parse_args()
    
    print("Vikunja Secure Deployment Script")
    print("="*40)
    
    # Step 1: Check prerequisites
    if not check_podman_available():
        sys.exit(1)
    
    # Step 2: Setup permissions
    if not setup_permissions():
        sys.exit(1)
    
    # Step 3: Setup secrets
    if not setup_secrets():
        sys.exit(1)
    
    # Step 4: Prune existing resources if requested
    if args.cleanup:
        prune_existing_resources()
    
    # Step 5: Deploy Vikunja
    if not deploy_vikunja():
        sys.exit(1)
    
    # Step 6: Wait for health
    if not wait_for_health():
        print("Warning: Services may not be fully ready. Check logs with:")
        print("podman-compose -f docker-compose.vikunja.yml logs")
    
    # Step 7: Run security scan
    if not args.skip_scan:
        run_security_scan()
    
    # Step 8: Display summary
    display_summary()


if __name__ == '__main__':
    main()