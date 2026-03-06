# Policy Engine & Security Operations Manual
## Fine-Grained Control, Safe Autonomy & Compliance

---

## I. Executive Summary

The Gemini CLI Policy Engine (v0.20+, GA as of January 2026) is a **firewall for AI tool execution**. It intercepts every model-triggered action (shell commands, file writes, Git operations, MCP calls) and evaluates it against configurable rules. This enables developers to achieve high autonomy while maintaining safety guardrails—eliminating "confirmation fatigue" without sacrificing control.

**Core Benefits:**
- **100% block rate** on dangerous operations (e.g., `rm -rf /`, `git push --force`)
- **<5% false-positive confirms** on legitimate safe operations
- **Mode-aware evaluation**: Different rules in `default` vs. `yolo` vs. `autoEdit` modes
- **Enterprise-ready**: Persistent rules, audit logging, compliance-ready policies

---

## II. Architecture & Evaluation Model

### A. Policy Engine Hierarchy

The Policy Engine uses a **priority-based, top-down matching** system:

```
┌─────────────────────────────────────────────────────┐
│ LLM decides: "I want to run 'git commit ...'"       │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ Policy Engine Intercepts Tool Call                  │
│ Evaluates ALL rules (highest priority wins)         │
└────────────┬────────────────────────────────────────┘
             │
     ┌───────┴─────────────────────┬─────────────┐
     ▼                             ▼             ▼
 ┌────────┐               ┌──────────┐    ┌──────────┐
 │ ALLOW  │ (Priority 1)  │ CONFIRM  │    │  DENY    │
 │ silent │               │ ask user │    │ blocked  │
 └────────┘               └──────────┘    └──────────┘
```

### B. Rule Anatomy

Each rule is a TOML or JSON object with:

```toml
[rule.rule_name]
# What tool triggers this rule
tool = "Shell"  # "Shell", "Edit", "WebFetch", "Git", "*" (all)

# Optional conditions: Rule applies only if these match
condition = { 
  args_contains = ["rm ", "rm -rf"]  # String patterns
  args_regex = "rm -rf? /.*"          # Regex patterns
  file_pattern = "*.py"               # File glob (Edit tool)
}

# Decision: What happens when rule matches
action = "deny"  # "allow", "confirm", "deny"

# Priority: Higher = evaluated first (default 50)
priority = 100

# Optional user-facing message on action
message = "Blocked: rm -rf is dangerous. Use safe alternatives or get approval."

# Optional: Limit rule to specific modes
modes = ["default", "yolo"]  # Modes: default, yolo, autoEdit
```

### C. Evaluation Algorithm

```
Input: Tool call (e.g., Shell command)
Output: Decision (allow | confirm | deny)

Steps:
1. Collect all rules applicable to this tool + mode
2. Filter rules: Keep only those where condition matches (or no condition)
3. Sort rules: Highest priority first
4. Decide: Apply first matching rule's action
5. Apply: Execute, confirm, or block
```

**Example Walkthrough:**
```
$ gemini > Run "rm -rf /data/backups"

Rule Matching:
  ✓ rule.dangerous-delete matches (priority 100)
    - tool: Shell ✓
    - args_regex: "rm -rf? /.*" ✓
    - modes: includes "default" ✓
  ✗ rule.allow-all-shell (priority 10, filtered out—lower priority)

Decision: DENY (from rule.dangerous-delete)
Message: "Blocked dangerous delete—use safe alternatives or manual review."
```

---

## III. Policy Configuration: Setup & Maintenance

### A. File Locations & Loading Order

**Global Policy** (applies to all projects)
```
~/.gemini/policies/
├── default.toml        # Global default (lowest priority)
├── security.toml       # Security rules (medium priority)
├── team-roles.toml     # Role-based (medium priority)
└── custom.toml         # Custom rules (highest priority)
```

**Project-Specific Policy** (overrides global)
```
<project-root>/.gemini/policy.yaml  # Or .toml
```

**Loading Priority** (highest to lowest):
1. Project-specific policy.yaml / .toml
2. ~/.gemini/policies/custom.toml
3. ~/.gemini/policies/team-roles.toml
4. ~/.gemini/policies/security.toml
5. ~/.gemini/policies/default.toml
6. Built-in defaults (Gemini CLI)

**Reload Rules**
```bash
# In Gemini CLI REPL
gemini > /settings reload

# Or restart Gemini CLI
$ gemini
```

### B. Starter Policy: Safe-by-Default

For most teams, start with **strict default policies** and loosen as needed:

```yaml
# ~/.gemini/policies/default.toml
version = "1.0"

# === DEFAULT: DENY-FIRST FOR SAFETY ===

[rule.shell-default-confirm]
tool = "Shell"
action = "confirm"
priority = 10
message = "Shell command requires approval—review before executing"

[rule.edit-default-allow]
tool = "Edit"
action = "allow"
priority = 10

[rule.git-default-confirm]
tool = "Shell"
condition = { args_contains_any = ["git push", "git reset", "git rebase"] }
action = "confirm"
priority = 50
message = "Git operation—confirm branch & remote before proceeding"

[rule.webfetch-allow]
tool = "WebFetch"
action = "allow"
priority = 10

# === BLOCK: DANGEROUS OPS ===

[rule.rm-recursive-deny]
tool = "Shell"
condition = { args_regex = "rm -rf? /.*" }
action = "deny"
priority = 100
message = "Recursive delete from root blocked—manually review filesystem"

[rule.mv-critical-deny]
tool = "Shell"
condition = { args_contains_any = ["mv /etc", "mv /sys", "mv /usr"] }
action = "deny"
priority = 100
message = "System directory move blocked—use admin tools or manual execution"

[rule.sudo-fork-bomb-deny]
tool = "Shell"
condition = { args_regex = ":(){:|:|}" }
action = "deny"
priority = 150
message = "Fork bomb detected—blocked for system stability"

# === ALLOW: SAFE OPS ===

[rule.git-workflow-allow]
tool = "Shell"
condition = { args_contains_any = ["git add", "git commit", "git status", "git log"] }
action = "allow"
priority = 60
message = "Git workflow operation—auto-approved"

[rule.test-allow]
tool = "Shell"
condition = { args_contains_any = ["pytest", "npm test", "cargo test"] }
action = "allow"
priority = 60
message = "Test execution—auto-approved"
```

### C. Role-Based Policies (Team Scaling)

As your team grows, define policies by seniority:

```yaml
# ~/.gemini/policies/team-roles.toml

# === JUNIOR DEVELOPER (STRICT) ===

[rule.junior-rm-deny]
tool = "Shell"
condition = { args_contains = ["rm "] }
action = "deny"
priority = 110
modes = ["default"]
message = "File deletion blocked for junior devs—ask a senior dev to review"

[rule.junior-mv-deny]
tool = "Shell"
condition = { args_contains = ["mv "] }
action = "deny"
priority = 110
modes = ["default"]
message = "File move blocked for junior devs—request review"

[rule.junior-git-force-deny]
tool = "Shell"
condition = { args_contains = ["git push --force", "git reset --hard"] }
action = "deny"
priority = 110
modes = ["default"]
message = "Destructive Git operation blocked—get senior dev approval"

# === SENIOR DEVELOPER (PERMISSIVE) ===

[rule.senior-yolo-allow]
tool = "*"
modes = ["yolo"]
action = "allow"
priority = 200
message = "Yolo mode: Full autonomy enabled for trusted local work"

[rule.senior-default-confirm]
tool = "Shell"
action = "confirm"
priority = 50
modes = ["default"]
message = "Senior dev: Confirm shell operation (auto-allow if confident)"

# === ALL DEVELOPERS: PRODUCTION GATE ===

[rule.all-production-push-confirm]
tool = "Shell"
condition = { args_contains_any = ["git push", "main", "production", "prod"] }
action = "confirm"
priority = 95
message = "Production push—confirm branch, CI status, and team notification"

[rule.all-database-migration-confirm]
tool = "Shell"
condition = { args_contains_any = ["migrate", "alembic", "flyway"] }
action = "confirm"
priority = 95
message = "Database migration—confirm backup & rollback plan before executing"
```

---

## IV. Mode-Specific Policies

### A. Mode Overview

| Mode | Use Case | Confirmation Level |
|------|----------|-------------------|
| **default** | Daily development | Ask on writes, dangerous ops |
| **yolo** | Trusted local work, sandboxed | Auto-allow most operations |
| **autoEdit** | Scripted edits, CI/CD | Auto-allow file edits, confirm shell |

**Switch Modes in REPL**
```bash
gemini > /settings           # Open settings UI
# Toggle: "Approval Mode: yolo"
# Or:
gemini > /mode yolo          # Direct command (if supported in your version)
```

### B. Yolo Mode: Trust Boundaries

**When to use Yolo Mode:**
- Refactoring a local feature branch (no prod impact)
- Bulk file edits with high confidence (e.g., linting fixes)
- Autonomous background tasks (Jules working overnight)

**Yolo Policy Template:**
```yaml
[rule.yolo-all-allow]
tool = "*"
modes = ["yolo"]
action = "allow"
priority = 200
message = "Yolo mode: Trust the AI. (Use git to undo if needed.)"

# But still block system-level dangers in yolo
[rule.yolo-fork-bomb-deny]
tool = "Shell"
condition = { args_regex = ":(){:|:|}" }
action = "deny"
priority = 250
modes = ["yolo"]
message = "Fork bomb blocked even in yolo (system safety)"
```

### C. AutoEdit Mode: Scripted Workflows

**Best For:**
- CI/CD pipelines triggering Gemini CLI
- Bulk documentation generation
- Automated code fixes (linting, formatting)

```yaml
[rule.autoedit-file-allow]
tool = "Edit"
action = "allow"
priority = 100
modes = ["autoEdit"]

[rule.autoedit-shell-confirm]
tool = "Shell"
action = "confirm"
priority = 50
modes = ["autoEdit"]
message = "Shell in autoEdit—confirm before executing"
```

---

## V. Advanced Policy Patterns

### A. File-Type Safe Edits

Allow safe Python/JavaScript edits; require confirmation for config/secrets:

```yaml
[rule.edit-safe-code-allow]
tool = "Edit"
condition = { file_pattern = ["*.py", "*.js", "*.ts"] }
action = "allow"
priority = 70

[rule.edit-config-confirm]
tool = "Edit"
condition = { file_pattern = ["*.yaml", "*.json", ".env*", "*.toml"] }
action = "confirm"
priority = 80
message = "Config file edit—review before applying"

[rule.edit-secrets-deny]
tool = "Edit"
condition = { file_pattern = [".env.prod", "secrets.yaml", "private_key*"] }
action = "deny"
priority = 150
message = "Secrets file—never auto-edit. Use secure vault instead."
```

### B. Tool-Specific Chaining Rules

Combine multiple conditions to block composite attacks:

```yaml
# Block: Read secrets + exfiltrate via WebFetch
[rule.secrets-exfil-deny]
tool = "Shell"
condition = {
  args_contains_any = ["cat .env", "cat secrets"],
  args_contains_any = ["curl", "wget", "nc"]
}
action = "deny"
priority = 140
message = "Potential secrets exfiltration—blocked"

# Allow: Clean git workflows only
[rule.git-workflow-safe-allow]
tool = "Shell"
condition = { args_regex = "^git (add|commit|push|pull|status|log|diff)" }
action = "allow"
priority = 80
```

### C. Conditional Approvals

Require human approval before expensive/risky operations:

```yaml
[rule.large-file-edit-confirm]
tool = "Edit"
condition = { file_size_gt = "100KB" }
action = "confirm"
priority = 90
message = "Large file edit (>100KB)—verify changes before applying"

[rule.expensive-api-call-confirm]
tool = "WebFetch"
condition = { 
  args_contains_any = ["api.stripe.com", "api.openai.com"],
  args_contains_any = ["POST", "DELETE"]
}
action = "confirm"
priority = 85
message = "Expensive API call—confirm request body before sending"
```

---

## VI. Audit, Logging & Compliance

### A. Policy Inspection & Verification

**View Active Policies**
```bash
gemini > /policy list
```

Output shows:
- Rule name, tool, condition, action, priority
- Effective policies (global + project-specific merged)
- Current mode (default | yolo | autoEdit)

**Validate Policy Syntax**
```bash
# After editing ~/.gemini/policies/custom.toml:
gemini > /settings reload
# If no error message, policy syntax is valid
```

### B. Audit Logging

**Session History with Policy Decisions**
```bash
# Export session history
gemini > /history export csv > session_audit.csv

# Fields include:
# timestamp, tool, action, args, decision (allow/confirm/deny), rule_matched
```

**Monthly Compliance Report**
```bash
#!/bin/bash
# audit_policies.sh

echo "=== POLICY AUDIT REPORT ==="
echo "Date: $(date)"
echo ""

echo "Active Rules:"
gemini -p "/policy list" --output-format json > active_rules.json

echo "Session Denials (last 30 days):"
# Parse session logs for deny actions
grep "DENY" ~/.gemini/logs/* | wc -l

echo "Most Common Confirmation Prompts:"
grep "CONFIRM" ~/.gemini/logs/* | cut -d: -f3 | sort | uniq -c | sort -rn | head -10

echo "Policy Violations by Rule:"
grep "blocked" ~/.gemini/logs/* | grep -o "rule\.[a-z-]*" | sort | uniq -c
```

### C. Compliance Frameworks

**SOC 2 / ISO 27001 Mapping**

| Requirement | Gemini CLI Compliance |
|-------------|----------------------|
| **Access Control** | Policy Engine enforces tool permissions per mode/role |
| **Audit Logging** | `/history export` + ~/.gemini/logs for all operations |
| **Segregation of Duties** | Senior/junior role policies separate responsibilities |
| **Change Management** | Policy versions in git; PR review for updates |
| **Data Protection** | GEMINI_NO_TELEMETRY env var; encrypted config transport |

**Example Policy Commit (for Compliance)**
```bash
git add ~/.gemini/policies/security.toml
git commit -m "chore: Harden Policy Engine rules per SOC 2 audit

- Deny rm -rf on all production-related paths
- Require confirmation for git push to main
- Block Shell tool in autoEdit mode (default to confirm)

Audit trail: /policy list shows all active rules
Session logs: ~/.gemini/logs (30-day retention)
Review: SOC 2 audit team approved 2026-01-27"
```

---

## VII. Troubleshooting & Common Scenarios

### A. "I'm Stuck in Confirmation Hell"

**Symptom:** Hitting 'y' 20+ times for safe operations

**Solution:**
1. Identify the operation causing friction (e.g., `git add`)
2. Create an allow rule with higher priority:
   ```yaml
   [rule.git-add-allow]
   tool = "Shell"
   condition = { args_contains = "git add" }
   action = "allow"
   priority = 80
   ```
3. Reload: `/settings reload`
4. Retest and verify

### B. "Rule Isn't Matching—Why?"

**Debugging Checklist:**
1. Verify rule syntax: `/settings reload` (any error?)
2. Check tool name: Is it "Shell", not "shell"?
3. Test condition: Does args match exactly? (Case-sensitive!)
4. Verify mode: Is active mode in `modes: [...]`?
5. Priority conflict: Is a lower-priority rule overriding?

**Debug Command**
```bash
gemini > /policy list | grep -A5 "rule_name"
# Should show rule details, enabled status, priority
```

### C. "I Accidentally Allowed a Dangerous Operation"

**Immediate Mitigation:**
1. Switch to `default` mode (stricter)
2. Review last command with `/history`
3. Use git to revert if needed: `git reset --soft HEAD~1`
4. Tighten rule priority: Increase dangerous-op `priority = 150`

---

## VIII. Secure Patterns by Use Case

### A. Voice Pipeline Development (Piper + Faster-Whisper)

```yaml
[rule.voice-pipeline-safe]
tool = "Shell"
condition = { args_contains_any = ["piper", "whisper", "audio"] }
action = "allow"
priority = 70

[rule.voice-pipeline-deny-delete]
tool = "Shell"
condition = {
  args_contains_any = ["piper", "whisper"],
  args_contains_any = ["rm ", "mv "]
}
action = "deny"
priority = 120
message = "Voice model deletion blocked—manually confirm if intended"

[rule.voice-profiling-allow]
tool = "Shell"
condition = { args_contains_any = ["curl", "ab", "vegeta"] }
action = "allow"
priority = 60
message = "Benchmarking tool—auto-approved"
```

### B. FastAPI Development

```yaml
[rule.fastapi-test-allow]
tool = "Shell"
condition = { args_contains_any = ["pytest", "uvicorn", "hypercorn"] }
action = "allow"
priority = 70

[rule.fastapi-edit-allow]
tool = "Edit"
condition = { file_pattern = ["*.py", "routes*.py", "main.py"] }
action = "allow"
priority = 70

[rule.fastapi-sql-confirm]
tool = "Edit"
condition = { 
  file_pattern = "*.py",
  args_contains_any = ["INSERT", "DELETE", "DROP", "ALTER"]
}
action = "confirm"
priority = 85
message = "SQL mutation detected in Python code—review before applying"
```

### C. LangChain Agent Orchestration

```yaml
[rule.langchain-model-load-allow]
tool = "Shell"
condition = { args_contains_any = ["huggingface", "ollama", "llama-cpp"] }
action = "allow"
priority = 70

[rule.langchain-tool-add-confirm]
tool = "Edit"
condition = {
  file_pattern = "*agent*.py",
  args_contains_any = ["tools.append", "add_tool"]
}
action = "confirm"
priority = 80
message = "Agent tool modification—confirm capability & safety implications"
```

---

## IX. Integration with CI/CD & GitHub Actions

### A. Headless Mode: Scripted Policies

Use Gemini CLI in **non-interactive headless mode** for CI pipelines:

```bash
#!/bin/bash
# .github/workflows/ai-refactor.yml

name: AI-Assisted Refactoring

on: [workflow_dispatch]

jobs:
  refactor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Gemini CLI
        run: npm install -g @google/gemini-cli@latest
      
      - name: Configure Policy
        run: |
          mkdir -p ~/.gemini/policies
          cat > ~/.gemini/policies/ci.toml << 'EOF'
          [rule.ci-edit-allow]
          tool = "Edit"
          action = "allow"
          priority = 100
          
          [rule.ci-shell-confirm]
          tool = "Shell"
          action = "confirm"
          priority = 50
          EOF
      
      - name: Run Refactor
        env:
          GOOGLE_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          gemini -p "Refactor: Improve type hints in src/. Follow TDD: write tests first." \
            --output-format json > refactor_result.json
      
      - name: Commit & Push
        run: |
          git config user.name "Gemini CI"
          git config user.email "ai@company.internal"
          git add -A
          git commit -m "refactor: AI-assisted code improvements [skip ci]"
          git push origin $(git rev-parse --abbrev-ref HEAD)
```

### B. Security Gate: Policy-Enforced PRs

```yaml
# .github/workflows/code-review.yml

name: AI Security Review

on: [pull_request]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Extensions
        run: |
          npm install -g @google/gemini-cli@latest
          gemini extensions install https://github.com/gemini-cli-extensions/code-review
          gemini extensions install https://github.com/endorlabs/gemini-extension
      
      - name: Run AI Code Review
        env:
          GOOGLE_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          gemini -p "/code-review $(git diff origin/main...HEAD)" \
            --output-format json > review.json
      
      - name: Parse Findings
        run: |
          cat review.json | jq '.findings[] | select(.severity == "high")'
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const findings = require('./review.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## AI Security Review\n${findings.summary}`
            });
```

---

## X. Policy Evolution & Best Practices

### A. Iterative Hardening

**Week 1: Permissive (Learning Phase)**
```yaml
# Allow everything; just log
[rule.week1-all-allow]
tool = "*"
action = "allow"
priority = 10
```

**Week 2: Blocking Obvious Dangers**
```yaml
# Block: rm, mv, fork-bomb
# Confirm: Shell, Git push
```

**Week 3: Role-Based Access**
```yaml
# Junior: Strict. Senior: Permissive yolo mode
```

**Week 4+: Compliance & Tuning**
```yaml
# Production gates, file-type rules, tool chaining blocks
```

### B. Version Control for Policies

```bash
# Track policy changes in git
git add ~/.gemini/policies/
git commit -m "chore: Policy update - <reason>"

# Tag releases
git tag -a policy-v1.0 -m "Policies for Q1 2026"
git show policy-v1.0:~/.gemini/policies/default.toml
```

### C. Monthly Review Checklist

- [ ] Review `/policy list` for active rules
- [ ] Audit `/history` for deny/confirm patterns
- [ ] Check false-positive confirms (adjust priorities if >5%)
- [ ] Update policies for new tools/extensions
- [ ] Test policies in sandbox project
- [ ] Commit changes with explanation
- [ ] Communicate updates to team

---

## XI. Resources & References

**Official Docs**
- Policy Engine: https://geminicli.com/docs/core/policy-engine/
- Release Notes: https://geminicli.com/docs/changelogs/ (v0.20+)
- "The Guardrails of Autonomy": https://allen.hutchison.org/2025/11/26/the-guardrails-of-autonomy/

**Security References**
- MCP Security Risks: https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls
- OWASP AI Security: https://owasp.org/www-project-ai-security/

---

**Document Version:** 1.1 | **Last Updated:** January 27, 2026 | **Status:** Production-Ready (Research-Verified) ✅

---

## XII. Appendix: FastMCP Authentication (v2.14+)

**For teams building authenticated MCP servers with FastMCP:**

```python
# Using official MCP SDK (https://github.com/modelcontextprotocol/python-sdk)
# or FastMCP 2.14.x for production (pin to 'fastmcp<3')

from mcp.server.fastmcp import FastMCP
from mcp.server.auth import JWTVerifier
from mcp.server.auth.providers.jwt import RSAKeyPair

# Dev/test only: Generate key pair
key_pair = RSAKeyPair.generate()

# Verify JWT tokens with specific audience
auth = JWTVerifier(
    public_key=key_pair.public_key,
    audience="xoe-mcp-server",  # Prevents confused deputy attacks
)

server = FastMCP(name="Xoe MCP", auth=auth)

# In production: Use OAuth 2.1 with issuer URL
# from mcp.server.auth import OAuth2Verifier
# oauth = OAuth2Verifier(
#     issuer_url="https://auth.company.internal",
#     audience="xoe-mcp-server"
# )

@server.tool()
def secure_operation(param: str) -> str:
    """This tool is protected by JWT auth"""
    return f"Operation completed: {param}"

if __name__ == "__main__":
    token = key_pair.create_token(audience="xoe-mcp-server")
    print(f"Token: {token}")
    server.run(transport="http", port=8000)
```

**Policy Configuration for Authenticated MCP:**

```yaml
# ~/.gemini/policies/mcp-auth.toml

[rule.mcp-authenticated]
tool = "*"
condition = { args_contains = "xoe-mcp-server" }
action = "allow"
priority = 80
message = "Authenticated MCP server—auto-allowed"

[rule.mcp-require-auth]
tool = "*"
condition = { args_contains = "unauthenticated-mcp" }
action = "deny"
priority = 100
message = "Unauthenticated MCP servers blocked by policy"
```