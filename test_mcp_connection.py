import asyncio
import subprocess
import json
import time

async def test_mcp_connection():
    try:
        # Start the MCP server in a subprocess
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
        time.sleep(2)

        # Send a simple initialization message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            }
        }

        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()

        # Read response
        response = process.stdout.readline()
        print("MCP Server Response:", response)

        # Clean up
        process.terminate()
        process.wait()

        return True
    except Exception as e:
        print("MCP Connection Test Failed:", e)
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())