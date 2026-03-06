---
description: "Scout for context and suggest tools for Opus handoff"
arguments:
  - name: task
    description: "The task to scout context for"
    required: true
---
I will act as a Context Scout for the task: "$task".
I will search for relevant files, read them into the session context, and suggest tools from the Omega Registry.

!python3 scripts/prepare_handoff_context.py "$task"
