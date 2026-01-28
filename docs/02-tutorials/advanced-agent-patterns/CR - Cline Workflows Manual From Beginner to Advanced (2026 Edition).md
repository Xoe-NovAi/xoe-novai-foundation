# **The Complete Cline Workflows Manual: From Beginner to Advanced (2026 Edition)**

## **Introduction: The Power of Cline Workflows**

Cline Workflows are Markdown files that define a series of steps to automate repetitive or complex development tasks directly within VS Code[reference:0]. Think of them as executable scripts for your AI assistant: you invoke a workflow with a simple slash command (e.g., `/pr-review.md`), and Cline meticulously follows the defined steps, using its tools, your CLI, and external services[reference:1].

**Workflows vs. Rules:** It's crucial to understand the distinction. **Rules** define *how* Cline should behave generally (e.g., "always use TypeScript strict mode") and are always active[reference:2]. **Workflows** define *what* specific task Cline should perform (e.g., "review this pull request") and are invoked on-demand[reference:3]. Using workflows for procedural tasks keeps your context window clean and tokens efficient[reference:4].

This manual will guide you from creating your first workflow to mastering advanced orchestration patterns used by top developers in 2026.

---

## **Part 1: Beginner – Your First Workflow**

### **1.1 Core Concepts & Structure**
A workflow is a standard Markdown file (.md) placed in a specific directory. Cline reads this file and executes the instructions step-by-step, leveraging its built-in tools[reference:5].

**Storage Locations:**
*   **Project-Specific:** `.clinerules/workflows/` in your project root.
*   **Global:** `~/Documents/Cline/Workflows/` (macOS/Linux) for cross-project use.
Project workflows take precedence if a name conflicts[reference:6].

### **1.2 Step-by-Step: The PR Review Workflow**
Let's build the canonical first workflow: an automated Pull Request reviewer.

1.  **Create the file:** Make `.clinerules/workflows/pr-review.md`.
2.  **Add the content:** Copy the following structured plan[reference:7].

    ```markdown
    # Pull Request Reviewer
    This workflow helps me review a pull request by analyzing the changes and drafting a review.

    ## 1. Gather PR Information
    First, I need to understand what this PR is about. I'll fetch the title, description, and list of changed files.
    ```bash
    gh pr view PR_NUMBER --json title,body,files
    ```

    ## 2. Examine Modified Files
    Now I will examine the diff to understand the specific code changes.
    ```bash
    gh pr diff PR_NUMBER
    ```

    ## 3. Analyze Changes
    I will analyze the code changes for:
    * **Bugs:** Logic errors or edge cases.
    * **Performance:** Inefficient loops or operations.
    * **Security:** Vulnerabilities or unsafe practices.

    ## 4. Confirm Assessment
    Based on my analysis, I will present my findings and ask how you want to proceed.
    ```xml
    <ask_followup_question>
    I've reviewed PR #PR_NUMBER. Here is my assessment:
    [Insert Analysis Here]
    Do you want me to approve this PR, request changes, or just leave a comment?
    ["Approve", "Request Changes", "Comment", "Do nothing"]
    </ask_followup_question>
    ```

    ## 5. Execute Review
    Finally, I will execute the review command based on your decision.
    ```bash
    # If approving:
    gh pr review PR_NUMBER --approve --body "Looks good to me! [Summary of analysis]"
    # If requesting changes:
    gh pr review PR_NUMBER --request-changes --body "Please address the following: [Issues list]"
    # If commenting:
    gh pr review PR_NUMBER --comment --body "[Comments]"
    ```
    ```

3.  **Run it:** In the Cline chat, type `/pr-review.md 42` (where 42 is your PR number)[reference:8].

**How It Works:** This workflow demonstrates key principles: it uses CLI commands (`gh`), directs Cline's analysis, incorporates human decision points, and completes the task. What used to take 15 minutes of manual work now happens with a single command[reference:9].

### **1.3 Let Cline Build Your Workflows**
The easiest way to start is to have Cline create workflows for you. After completing a task, simply say: **"Cline, create a workflow for the process I just completed."** It will analyze the conversation, identify the steps, and generate a properly structured file[reference:10].

There's even a meta-workflow to guide you: save `create-new-workflow.md` to your workflows directory and run it. Cline will ask for the purpose, objective, and major steps, then generate the file for you[reference:11].

---

## **Part 2: Intermediate – Tools, Design, and Best Practices**

### **2.1 Essential Built-in Tools**
Powerful workflows use Cline's tools explicitly. Here are the most common ones[reference:12]:

| Tool                    | Purpose                                                      | Example                                              |
| :---------------------- | :----------------------------------------------------------- | :--------------------------------------------------- |
| `execute_command`       | Runs any CLI command.                                        | `npm run test`                                       |
| `read_file`             | Reads file contents for analysis.                            | `src/config.json`                                    |
| `write_to_file`         | Creates or overwrites files.                                 | `src/components/Button.tsx`                          |
| `search_files`          | Searches for regex patterns across files.                    | `src/ TODO *.ts`                                     |
| `ask_followup_question` | Pauses for user input/confirmation.                          | `Do you want to deploy to production? ["Yes", "No"]` |
| `browser_action`        | Controls a built-in browser to interact with websites or local servers. | `launch http://localhost:3000`                       |

**Best Practice:** Be specific. Instead of "find the user controller," write: **"Use `search_files` to look for `UserController` in the `src/controllers` directory."**[reference:13]

### **2.2 Workflow Design Principles**
*   **Start Simple:** Begin with small, single-task workflows. Combine them later as you get comfortable[reference:14].
*   **Be Modular:** Break complex tasks into smaller, reusable workflows. This makes them easier to maintain and debug[reference:15].
*   **Use Clear Comments:** Explain *why* a step is happening, not just *what*. This helps both you and Cline understand the intent[reference:16].
*   **Version Control:** Treat workflows as code. Store them in your Git repository (in `.clinerules/workflows/`) so they are versioned, reviewed, and shared with your team[reference:17].

### **2.3 Example: Deployment Workflow**
A deployment workflow showcases orchestrating multiple tools[reference:18].

```markdown
# Deploy to Staging
This workflow validates, builds, and deploys the application to a staging environment.

1. **Run Tests**
   ```bash
   npm test
```

2. **Build Application**
   ```bash
   npm run build
   ```

3. **Deploy with Docker**
   ```bash
   podman build -t my-app:staging .
   podman push my-registry/my-app:staging
   kubectl apply -f k8s/staging/
   ```

4. **Health Check**
   ```bash
   curl -f http://staging.my-app.com/health || exit 1
   ```

5. **Notify Team**
   *Use the Slack MCP server to post a notification to the #engineering channel.*

6. **Confirm for Production**
   ```xml
   <ask_followup_question>
   Staging deployment is healthy. Proceed with production deployment?
   ["Yes", "No"]
   </ask_followup_question>
   ```
```

---

## **Part 3: Advanced – Integration, Logic, and Meta-Workflows**

### **3.1 Integrating MCP (Model Context Protocol) Tools**
MCP servers connect Cline to external services (GitHub, Slack, Databases). You can reference them naturally or with explicit XML tags for deterministic control[reference:19].

**Natural Language (Simple):**
> "Fetch the latest issues from the github-repo MCP server. Summarize the critical bugs. Post the summary to #engineering using the slack-notifications MCP."

**Explicit XML (Deterministic):**
```xml
<use_mcp_tool>
github-repo-manager create_issue {
  "owner": "cline",
  "repo": "cline",
  "title": "Automated Bug Report",
  "body": "Found a regression in the latest build."
}
</use_mcp_tool>
```

### **3.2 Conditional Logic and Error Handling**
Advanced workflows can branch based on outcomes. While Cline doesn't have a formal IF/ELSE DSL, you can design steps to create conditional paths.

**Pattern: Ask & Branch**
```markdown
4. **Validate Build**
   ```bash
   mkdocs build --strict
```
5. **Check Outcome**
   If the build fails, ask the user:
   "The documentation build failed. Should I attempt to fix it automatically, or would you like to review the errors first?"
   ["Fix automatically", "Show errors"]
```

**Pattern: Pre-Flight Check**
Use `execute_command` to check a condition (e.g., `git status --porcelain`) and instruct Cline to stop or branch its analysis based on the output.

### **3.3 Hooks: Injecting Custom Logic (v3.36+)**
For ultimate control, **Hooks** let you inject custom scripts (bash, Python, etc.) at key moments in Cline's workflow[reference:20].

**How it works:** Place executable scripts in `~/Documents/Cline/Rules/Hooks/` (global) or `.clinerules/hooks/` (project). The script receives JSON context via stdin and can cancel the operation or modify Cline's context[reference:21].

**Example Hook Types[reference:22]:**
*   **PreToolUse:** Validate an action *before* it runs (e.g., block creation of `.js` files in a TypeScript project).
*   **PostToolUse:** Learn from completed actions (e.g., track performance metrics).
*   **UserPromptSubmit:** Inject context based on user prompts.

### **3.4 Meta-Workflows: Workflows That Improve Your Setup**
The most powerful pattern is the self-improving workflow. For example, a workflow that:
1.  Analyzes your recent Cline session history.
2.  Identifies repetitive corrections or successful patterns.
3.  Proposes updates to your `.clinerules` or suggests new workflows.
4.  Asks for your approval to implement the changes.

This creates a feedback loop where your AI assistant actively helps refine its own instructions[reference:23].

### **3.5 Managing Context and Token Limits**
Workflows are token-efficient as they are only injected when invoked[reference:24]. However, long workflows processing large outputs can hit limits.

**Strategies[reference:25]:**
*   **Break It Down:** Split long processes into smaller, chained workflows.
*   **Be Concise:** Keep instructions clear and to the point.
*   **Summarize Mid-Process:** For workflows that analyze large logs, instruct Cline to summarize sections before proceeding.

---

## **Part 4: Expert Patterns & Real-World Examples**

### **4.1 The Database Migration Workflow**
A robust workflow for safe, documented schema changes[reference:26].

```markdown
# Database Migration
1. **Create Migration File:** Generate a timestamped SQL file in `/supabase/migrations/`.
2. **Review with Cline:** Have Cline analyze the SQL for potential issues (e.g., missing indexes, locking).
3. **Dry-Run Locally:** Apply the migration to a local test database.
4. **Run Tests:** Execute integration tests that depend on the schema.
5. **Update Documentation:** Automatically update `schema.md` with the new structure.
6. **Notify Team:** Post a summary of the change to the team's chat channel.
```

### **4.2 The Component Factory**
Standardize the creation of new UI components.

```markdown
# New React Component
1. **Gather Specs:** Ask for the component name and type (e.g., `Button`, `Modal`).
2. **Generate Files:** Create `ComponentName.tsx`, `ComponentName.stories.tsx`, `ComponentName.test.tsx`, and `index.ts` barrel file.
3. **Add to Index:** Update the parent `index.ts` to export the new component.
4. **Open for Edit:** Present the main component file for final tweaks.
```

### **4.3 Daily Development Starter**
A personal workflow to begin the day.

```markdown
# Morning Setup
1. **Pull Latest Changes:** `git pull origin main`
2. **Check Issues:** Fetch and list open issues assigned to you from GitHub.
3. **Review Yesterday's Logs:** Read `memory_bank/activeContext.md` to resume context.
4. **Set Daily Goal:** Prompt you to state your primary goal for the day.
```

---

## **Conclusion: From Automation to Transformation**

Cline Workflows evolve your role from a manual executor to a **automation designer**. The journey begins with automating a single tedious task and progresses to encoding your team's best practices into executable, shareable knowledge.

**Your Action Plan:**
1.  **Today:** Run the `/create-new-workflow.md` meta-workflow or ask Cline to build a workflow for a task you just finished.
2.  **This Week:** Create 3-5 core workflows for your most repetitive tasks (PR reviews, deployments, component generation).
3.  **This Month:** Explore MCP integrations and implement a Hook for a critical safety check (e.g., validating production deployments).
4.  **Ongoing:** Cultivate a library of workflows. Share them with your team. Let them evolve. The most powerful workflows emerge from real, daily problems[reference:27].

By mastering workflows, you're not just using an AI assistant—you're building an **autonomous engineering partner** tailored to your unique workflow and stack.