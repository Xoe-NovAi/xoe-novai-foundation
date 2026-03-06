To make MCP servers work in VSCode (or the compatible editor Codium), you need to create a specific JSON configuration file. This file tells your editor how to find and start the server you've installed.

Here is the essential information for setting it up.

### **📍 File Location and Core Structure**
Your configuration must be placed in a `.vscode/mcp.json` file within your workspace folder. The basic structure is as follows:

```json
{
  "servers": {
    "your-server-name": {
      "command": "executable-name",
      "args": ["arg1", "arg2"],
      "env": {
        "API_KEY": "your-secret-key"
      }
    }
  }
}
```

| Field                    | Description & Tips                                           |
| :----------------------- | :----------------------------------------------------------- |
| **`"your-server-name"`** | A unique name for your server (e.g., `"github-mcp"`, `"json-mcp-server"`). |
| **`"command"`**          | The executable to run (e.g., `"npx"`, `"python"`, `"uv"`). Use the absolute path if the command isn't in your system's PATH. |
| **`"args"`** (Optional)  | An array of arguments passed to the command (e.g., a server script name or CLI flags). |
| **`"env"`** (Optional)   | Environment variables for the server, often used for API keys. **Never hardcode real secrets here—use input variables instead**. |

### **🔧 Configuration Types and Examples**
MCP servers typically connect in one of two ways. The `"type"` field in your JSON tells VSCode which method to use.

| Type                   | Purpose                                                      | Example Configuration                                        |
| :--------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| **`"stdio"`**          | For servers that run locally on your machine as a command-line program. This is common for servers installed via `npm` or `pip`. | ```json<br>{<br>  "servers": {<br>    "json-mcp-server": {<br>      "command": "npx",<br>      "args": ["json-mcp-server@latest"]<br>    }<br>  }<br>}``` |
| **`"http"` / `"sse"`** | For servers that are hosted remotely and accessible via a URL. | ```json<br>{<br>  "servers": {<br>    "omni-mcp": {<br>      "url": "https://your-instance.omniapp.co/mcp/https"<br>    }<br>  }<br>}``` |

If the `"type"` field is omitted, VSCode will usually try to auto-detect it based on whether you provided a `"command"` or a `"url"`.

### **⚙️ How to Configure and Activate a Server**
You can create and edit the `mcp.json` file manually, or use VSCode's built-in commands for guidance:

1.  **Open the Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`).
2.  Type and run **`"MCP: Add Server"`**.
3.  Follow the prompts to select the server type (`stdio` or `http`/`sse`), provide the command/URL, and name your server.
4.  Choose **`"Workspace"`** to save the configuration to your project's `.vscode/mcp.json` file.

After configuring, you need to start the server:

1.  Open the Command Palette again.
2.  Run **`"MCP: List Servers"`**, then select your server from the list and choose **`"Start Server"`**.
3.  A success message like `"Discovered X tools"` should appear in the output panel. You can now use the server's tools in the Copilot chat.

### **🚀 Using MCP Servers and Troubleshooting**
Once a server is running, its tools become available in the Copilot Chat panel when you use **Agent Mode**. You can select which tools are active via the tool picker (the wrench icon).

**Common Issues and Fixes:**
*   **Server not showing up/starting**: Double-check the paths in your `"command"` and `"args"`—they often need to be **absolute paths**, not relative ones.
*   **"Command not found" errors**: Ensure the program (like `npx`, `python`, or `uv`) is installed and available in your system's terminal.
*   **Clearing cached tools**: If you update a server but don't see new tools, run the **`"MCP: Reset Cached Tools"`** command.

**A Note on Codium**: As a binary-compatible fork of VSCode, Codium should support MCP servers in the same way. The configuration process and file location are identical.

If you can share the name or type of MCP server you're trying to configure (e.g., a local Python script or a hosted service), I might be able to offer more specific guidance.