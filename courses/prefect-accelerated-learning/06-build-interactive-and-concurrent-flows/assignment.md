---
slug: build-interactive-and-concurrent-flows
id: 2rxwdzsxidhv
type: challenge
title: Build Interactive and Concurrent Flows
teaser: Combine pause-based human input with threadpool concurrency in a local Prefect
  workflow.
notes:
- type: text
  contents: |-
    # What PAL 106 adds

    Module 106 extends the workflow toolbox with human-in-the-loop pauses, concurrency,
    prioritization, advanced triggers, and workflow testing. The common theme is that
    once workflows are observable, you can make them interactive and more responsive to
    real operating conditions.
- type: text
  contents: |-
    # Local-first focus

    This lab uses two examples from the PAL materials that work well locally: pausing a
    run for user input and using `ThreadPoolTaskRunner` to run multiple tasks at once.
tabs:
- id: d3gsbpiwyj5b
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: 4pk5nd0phjsk
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: e4damulnte2g
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
# Build Interactive and Concurrent Flows

This challenge adapts the most practical local patterns from PAL 106.

## Step 1: Create an interactive flow

Create `/root/pal/interactive_and_concurrent.py` with a flow named `greet_user` that:

- uses `pause_flow_run(wait_for_input=str)`
- prints a greeting after input is supplied

## Step 2: Add concurrent task execution

In the same file, add:

- a task named `stop_at_floor`
- a flow named `elevator`
- `ThreadPoolTaskRunner(max_workers=2)`
- `wait(...)` on the submitted futures

Follow the PAL example and submit tasks for floors 3, 2, and 1.

## Step 3: Run the concurrent example

In the `__main__` block, run `elevator()` so the script finishes automatically when you
test it:

```run
cd /root/pal
uv run interactive_and_concurrent.py
```

Optionally, switch the entrypoint to `greet_user()` for a manual test in the UI.

## Verify

Before clicking **Check**, make sure:

- the script uses `pause_flow_run`
- the script uses `ThreadPoolTaskRunner`
- the script submits tasks and waits for them
- running the script completes the concurrent flow
