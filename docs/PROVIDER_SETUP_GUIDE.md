# ☁️ Omega Stack Provider Setup Guide

**Version**: 1.0.0
**Date**: March 4, 2026
**Status**: ACTIVE

---

## 📖 Overview

This guide provides step-by-step instructions for setting up and configuring external AI providers within the Omega Stack. While we prioritize local-first models, external providers like **SiliconFlow** and **SambaNova** offer access to massive frontier models (DeepSeek R1, Llama 3.1 405B) with generous free tiers.

---

## 🚀 SiliconFlow (DeepSeek V3/R1)

SiliconFlow provides high-speed access to DeepSeek models with a very generous free trial.

### 1. Preliminary Steps
1.  **Create Account**: Visit [cloud.siliconflow.cn](https://cloud.siliconflow.cn/) and sign up. You can use Email/SMS or OAuth (GitHub/Google).
2.  **Verify**: Complete verification to unlock trial credits.
3.  **Get API Key**: Navigate to the **"API Keys"** section in the sidebar and click **"Create API Key"**.
4.  **Copy Key**: Copy the key immediately; it will not be shown again.

### 2. Integration
Run the following Omega Stack command to inject the key:
```bash
make provider-setup-silicon
```
*You will be prompted to paste your key. This script updates your local `auth.json` automatically.*

---

## ⚡ SambaNova (Llama 3.1 405B)

SambaNova Cloud offers extremely fast inference for open-source models.

### 1. Preliminary Steps
1.  **Create Account**: Visit [cloud.sambanova.ai](https://cloud.sambanova.ai/) and sign up.
2.  **Verify**: Verify your email to access the dashboard.
3.  **Get API Key**: Go to **"APIs"** in the sidebar and click **"Create API Key"**.
4.  **Copy Key**: Store this key securely.

### 2. Integration
Run the following Omega Stack command:
```bash
make provider-setup-sambanova
```
*This will inject the key into your sovereign credential store.*

---

## 🛠️ Maintenance & Diagnostics

We provide automated tools to ensure your provider integrations stay healthy.

### Health Checks
To check the status of all configured accounts (including Antigravity and Cloud providers):
```bash
make antigravity-status
# OR
./scripts/antigravity-maintenance.sh status
```

### Credential Synchronization
If you update a key, ensure it is synchronized across all 8 isolated Omega instances:
```bash
make antigravity-sync
```

### Log Management
Debug logs for provider interactions are stored in `~/.config/opencode/antigravity-logs/`. To clean up old logs:
```bash
./scripts/antigravity-maintenance.sh cleanup
```

---

## ❓ FAQ & Troubleshooting

### Q: Why does it say "API Key Missing"?
**A:** Ensure you have run the `make provider-setup-...` command. Check your `~/.local/share/opencode/auth.json` to verify the key is present.

### Q: Do I need to use OAuth for these?
**A:** No. While Antigravity uses OAuth, SiliconFlow and SambaNova currently use **Static API Keys**. Our system handles both seamlessly in the background.

### Q: How do I add a provider not listed here?
**A:** Add it to the `OMEGA_TOOLS.yaml` registry and create a corresponding `make` target following the pattern in the `Makefile`.

---

## 🔗 Related Documentation
- [Antigravity Sovereign Operations](./ANTIGRAVITY_SOVEREIGN_OPS.md)
- [OpenCode Multi-Account Guide](./OPENCODE_MULTI_ACCOUNT_GUIDE.md)
- [Architecture Overview](../memory_bank/ARCHITECTURE.md)

## 🔄 Multi-Account Rotation (SiliconFlow & SambaNova)

The Omega Stack supports automatic rotation across 3 separate accounts for SiliconFlow and SambaNova to triple your free tier quotas.

### Setup Instructions
1.  **Obtain 8 Keys**: Sign up for each provider using 8 different email addresses.
2.  **Edit Environment**: Open `~/.config/xnai/.env` and fill in your keys. Use the account labels to stay organized:
    ```bash
    # --- ACCOUNT 1: your.email@gmail.com ---
    export SAMBANOVA_API_KEY_1="sk-..."
    export SILICONFLOW_API_KEY_1="sk-..."
    export GEMINI_API_KEY_1="AIza..."
    ```
3.  **Provision**: Run the command to lock them into their respective instances:
    ```bash
    make provision
    ```

The system will automatically assign each account to its dedicated Omega instance (1-to-1 mapping).

## 🔄 Multi-Account Power (8 Accounts)

The Omega Stack is now optimized for your 8 unique email accounts. Each account is assigned to a dedicated Omega instance (1-to-1 mapping).

### Final Setup
1.  **Edit Environment**: Fill in all 8 keys for each provider in `~/.config/xnai/.env`.
2.  **Provision**: Run the command to lock them into their respective instances:
    ```bash
    ./scripts/antigravity-maintenance.sh provision
    ```

### How to use a specific account:
To use **Account 3**, simply set the instance ID in your command:
```bash
XDG_DATA_HOME=/tmp/xnai-opencode-instance-3 opencode run "Your prompt" --model siliconflow/deepseek-ai/DeepSeek-V3
```

## 🏆 Top 5 SambaNova Models for the Omega Stack

1.  **Meta-Llama-3.1-405B-Instruct**: Deep reasoning, complex coding, and high-tier architecture tasks.
2.  **Meta-Llama-3.3-70B-Instruct**: Best-in-class general purpose assistant with high speed.
3.  **DeepSeek-R1**: Specialized reasoning and math performance matching OpenAI o1.
4.  **Qwen2.5-72B-Instruct**: Excellent for multilingual and specialized coding tasks.
5.  **Whisper-Large-v3**: Ultra-low-latency, high-accuracy speech-to-text (Integrated into Nova Voice).

## ♊ Gemini CLI Multi-Account & Domain Experts

The Omega Stack uses a **Sovereign Dispatcher** to manage your 8 Google accounts. Each account is assigned a dedicated "Domain Expert" instance with isolated history and memory.

### Domain Mapping
| Instance | Domain | Description |
| :--- | :--- | :--- |
| 1 | **Architect** | High-level stack context and READMEs |
| 2 | **API** | FastAPI, anyio, and backend logic |
| 3 | **UI/Frontend** | Chainlit and Dashboard development |
| 4 | **Voice/Audio** | SambaNova Whisper and local audio |
| 5 | **Data/Gnosis** | Postgres, Qdrant, and GraphRAG |
| 6 | **Sovereign Ops** | Podman, Make, and Security |
| 7 | **Research** | Ingestion and Crawl4AI |
| 8 | **Testing/QA** | Validation and quality handoffs |

### How to use
1.  **Install Dispatcher**: Run `make gemini-dispatcher-install` and then `source ~/.bashrc`.
2.  **Run by Domain**: 
    ```bash
    gemini --arch "Review the README.md"
    gemini --api "Debug this FastAPI endpoint"
    ```
3.  **Run with Rotation** (for quota): 
    ```bash
    gemini --rotate "A long task that needs fresh quota"
    ```
