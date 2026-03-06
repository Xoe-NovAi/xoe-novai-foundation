Here is a comprehensive, best-practice guide for integrating Google’s Gemini CLI with your Codium environment to power the Cline AI assistant via the command line. The recommended approach uses the standalone **Cline CLI** as the bridge between the Codium extension and Gemini, as direct “Gemini CLI” provider support in the extension may be unstable[reference:0].

---

## 📋 Prerequisites
*   **Node.js 20+** and **npm** (for installing CLI tools).
*   **VSCodium** (the open-source VS Code variant) installed.
*   A **Google account** (for Gemini CLI authentication) or a **Gemini API key**.

---

## 🛠️ Step 1: Install & Authenticate Gemini CLI
Gemini CLI provides the core AI model access. Install it globally and set up authentication.

| Action                                 | Command / Instruction                                        | Reference     |
| -------------------------------------- | ------------------------------------------------------------ | ------------- |
| **Install**                            | `npm install -g @google/gemini-cli`                          | [reference:1] |
| **Authenticate (OAuth – recommended)** | Run `gemini` and follow the browser prompt to log in with your Google account. This grants the free tier (60 req/min, 1,000 req/day). | [reference:2] |
| **Authenticate (API key)**             | Alternatively, set `export GEMINI_API_KEY="your_key"` (from [Google AI Studio](https://aistudio.google.com/apikey)). | [reference:3] |
| **Verify**                             | Run `gemini -p "Hello"` to confirm installation and authentication. | –             |

---

## 🖥️ Step 2: Install & Configure Cline CLI
The Cline CLI is a standalone service that can use Gemini as its AI provider and can be called by the Codium extension.

| Action                 | Command / Instruction                                        | Reference     |
| ---------------------- | ------------------------------------------------------------ | ------------- |
| **Install**            | `npm install -g cline`                                       | [reference:4] |
| **Configure Provider** | Run `cline auth` and select **Google Gemini** from the interactive list. If prompted, provide your Gemini API key or allow OAuth flow (the CLI will reuse your Gemini CLI credentials if possible). | [reference:5] |
| **Test CLI**           | Run `cline "List files in this directory"` to verify the CLI works and uses Gemini. | –             |

> 💡 **Note:** The Cline CLI supports multiple providers; ensure “Google Gemini” is selected. The free tier limits (60 req/min, 1,000 req/day) apply when using the same Google account[reference:6].

---

## ⚙️ Step 3: Install Codium & Cline Extension
Set up the IDE and the Cline extension.

| Action                      | Instruction                                                  | Reference     |
| --------------------------- | ------------------------------------------------------------ | ------------- |
| **Install Codium**          | Download from [vscodium.com](https://vscodium.com) and install. | –             |
| **Install Cline Extension** | In Codium, open **Extensions** (Ctrl+Shift+X), search for “Cline”, and install the official extension. | [reference:7] |
| **Sign In (Optional)**      | The extension may prompt you to sign in to a Cline account. This is optional if you plan to use the CLI backend. | [reference:8] |

---

## 🔗 Step 4: Integrate Cline Extension with Cline CLI
The key integration is enabling the extension to delegate tasks to the Cline CLI, which already uses Gemini.

| Action                          | Instruction                                                  | Reference      |
| ------------------------------- | ------------------------------------------------------------ | -------------- |
| **Ensure CLI is reachable**     | The extension automatically detects the globally installed `cline` command. Verify by opening a terminal in Codium and typing `cline --version`. | –              |
| **Delegate tasks**              | When you start a task in the Cline extension, it can **call the Cline CLI** to execute the task with a fresh context window. This delegation is built into the extension[reference:9]. |                |
| **Configure Terminal Settings** | In Cline’s settings (click the gear icon in the Cline chat), go to **Terminal Settings** and ensure **Background Execution Mode** is enabled for smoother integration. | [reference:10] |

> 🚨 **Important:** If the extension’s provider list includes “Gemini CLI,” you can select it directly. However, this option has been reported to disappear in recent updates[reference:11]. Using the Cline CLI with Google Gemini is the more stable approach.

---

## ✅ Step 5: Verify the Complete Workflow
Test that the entire chain works.

1.  **Open Codium** and launch the Cline panel (click the Cline icon in the activity bar).
2.  **Start a simple task**, e.g., “Create a Python function to calculate factorial.”
3.  **Observe the process**:
    *   The extension may delegate the task to the Cline CLI (you might see terminal activity).
    *   The Cline CLI uses the Gemini provider to generate the code.
    *   The result is displayed in the Cline chat panel.
4.  **Check the CLI directly** by opening a terminal in Codium and running `cline "What is 5 factorial?"` to confirm Gemini is responding.

---

## 📚 Best Practices & Troubleshooting

| Area                      | Recommendation                                               |
| ------------------------- | ------------------------------------------------------------ |
| **Rate Limits**           | The free Gemini tier allows 60 requests/minute and 1,000 requests/day. Monitor usage to avoid throttling. |
| **Security**              | Prefer OAuth login for personal use; for shared environments, use API keys stored in environment variables. |
| **Updates**               | Keep tools updated: `npm update -g @google/gemini-cli cline`. |
| **Provider Missing**      | If “Gemini CLI” is missing in the extension, use the Cline CLI + Google Gemini provider as described above. |
| **Terminal Issues**       | If Cline cannot execute commands, check the **Terminal Integration Troubleshooting Guide**[reference:12]. |
| **Authentication Errors** | Re-run `gemini` or `cline auth` to refresh tokens. Ensure your Google account has Gemini API access enabled. |
| **High Resource Usage**   | The Cline Core service runs in the background. Manage instances with `cline instance list` and `cline instance kill` if needed. |

---

## 🎯 Summary
By following this manual, you have established a robust integration where:
1.  **Gemini CLI** serves as the AI engine.
2.  **Cline CLI** acts as the scriptable agent that uses Gemini.
3.  **Codium + Cline extension** provides the IDE interface, delegating tasks to the Cline CLI.

This architecture leverages the strengths of each component and is the recommended best practice for a seamless, terminal‑first AI‑assisted development workflow in Codium.