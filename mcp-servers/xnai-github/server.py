import os
import subprocess
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("XNAi-GitHub")

def run_git_command(args):
    """Executes a git command and returns the output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

@mcp.tool()
def git_status():
    """Returns the current status of the git repository."""
    return run_git_command(["status"])

@mcp.tool()
def git_add(files: list[str]):
    """Adds files to the git staging area."""
    return run_git_command(["add"] + files)

@mcp.tool()
def git_commit(message: str):
    """Commits staged changes with a message."""
    return run_git_command(["commit", "-m", message])

@mcp.tool()
def git_push(remote: str = "origin", branch: str = "main"):
    """Pushes committed changes to the remote repository."""
    return run_git_command(["push", remote, branch])

@mcp.tool()
def git_pull(remote: str = "origin", branch: str = "main"):
    """Pulls changes from the remote repository."""
    return run_git_command(["pull", remote, branch])

@mcp.tool()
def git_log(count: int = 5):
    """Returns the last N commit messages."""
    return run_git_command(["log", "-n", str(count), "--oneline"])

if __name__ == "__main__":
    mcp.run()
