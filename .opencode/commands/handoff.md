---
description: "Prepare context for handoff to Opus 4.6"
arguments:
  - name: task
    description: "The task description for Opus"
    required: true
---
I will prepare the handoff context for the task: "$task"

!python3 scripts/prepare_handoff_context.py "$task"
