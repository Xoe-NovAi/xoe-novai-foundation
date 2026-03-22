import subprocess
import sys

branches = [
    "remotes/origin/audit/service-orchestrator-lazy-init",
    "remotes/origin/feature/multi-account-hardening",
    "remotes/origin/phase5a/account-naming-onboarding",
    "remotes/origin/phase5a/rollback-automation",
    "remotes/origin/xnai-agent-bus/harden-infra"
]

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def get_root_commit(branch):
    return run_command(f"git rev-list --max-parents=0 {branch}")

def get_files(branch):
    output = run_command(f"git ls-tree -r --name-only {branch}")
    if output.startswith("Error"):
        return set()
    return set(output.splitlines())

def analyze():
    print("Analyzing branches against 'develop'...")
    develop_root = get_root_commit("develop")
    develop_files = get_files("develop")
    
    print(f"Develop Root: {develop_root}")
    print(f"Develop File Count: {len(develop_files)}")
    print("-" * 30)

    for branch in branches:
        print(f"Branch: {branch}")
        root = get_root_commit(branch)
        print(f"  Root Commit: {root}")
        
        if root != develop_root:
            print("  STATUS: Unrelated History (Different Root)")
        else:
            print("  STATUS: Related History (Same Root)")

        branch_files = get_files(branch)
        unique_files = branch_files - develop_files
        
        # files present in both but maybe different content? 
        # Checking hash would be too slow for all, but let's see if we can just list unique names first.
        
        print(f"  Total Files: {len(branch_files)}")
        print(f"  Unique Files (not in develop): {len(unique_files)}")
        
        if len(unique_files) > 0:
            print("  Top 10 Unique Files:")
            for f in list(unique_files)[:10]:
                print(f"    {f}")
            if len(unique_files) > 10:
                print("    ...")

        print("-" * 30)

if __name__ == "__main__":
    analyze()
