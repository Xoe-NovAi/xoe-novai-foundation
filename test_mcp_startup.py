import subprocess
import time

def test_mcp_startup():
    try:
        # Start the MCP server
        process = subprocess.Popen(
            [
                ".venv_mcp/bin/python3",
                "mcp-servers/memory-bank-mcp/server.py",
                "--stdio"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give it a moment to initialize
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            print("MCP Server started successfully!")
            process.terminate()
            return True
        else:
            print("MCP Server failed to start")
            return False
    except Exception as e:
        print("MCP Startup Test Failed:", e)
        return False

if __name__ == "__main__":
    test_mcp_startup()