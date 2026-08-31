---
slug: explore-bonus-patterns
id: bljofy9bjef8
type: challenge
title: Explore Bonus Patterns
teaser: Use PAL bonus material to combine transactions, hooks, and control-oriented
  workflow patterns.
notes:
- type: text
  contents: |-
    # Bonus material in PAL

    The Bonus folder expands on the main modules with additional patterns like client
    usage, control-flow experiments, state hooks, REST-oriented flows, and transaction
    examples. These are useful once the core flow lifecycle feels comfortable.
- type: text
  contents: |-
    # Appendix-style goal

    This final challenge is intentionally optional in spirit. It packages a few bonus
    ideas into one local exercise so you can practice advanced control over workflow
    behavior without changing the core track progression.
tabs:
- id: 9yo8qqirtesy
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: 3zf52ikmymdg
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: iuw8yydodugq
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: advanced
timelimit: 900
enhanced_loading: null
---
# Explore Bonus Patterns

This appendix challenge combines ideas from PAL's Bonus examples.

## Step 1: Create a transactional flow

Create `/root/pal/bonus_patterns.py` with:

- a task named `write_side_effect`
- a rollback hook that removes a file if the transaction fails
- a task named `validate_contents`
- a flow named `bonus_pipeline`

Use `with transaction():` inside the flow.

## Step 2: Add a completion hook

Add either an `on_completion` flow hook or a final log message that makes it obvious
when the run succeeds. The goal is to practice attaching workflow behavior to lifecycle
events, which is a recurring theme in the bonus material.

## Step 3: Exercise the rollback path

Have `bonus_pipeline` call `validate_contents` on a single-line string so validation
fails and the side-effect file is cleaned up.

## Verify

Before clicking **Check**, make sure:

- the script imports `transaction`
- it defines a rollback hook
- it validates a file-based side effect
- the failed run does not leave `bonus-side-effect.txt` behind
