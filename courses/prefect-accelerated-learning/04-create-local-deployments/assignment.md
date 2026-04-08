---
slug: create-local-deployments
id: uk0tuwstxgfu
type: challenge
title: Create Local Deployments
teaser: Learn PAL deployment concepts by creating a local process deployment backed
  by a work pool.
notes:
- type: text
  contents: |-
    # What PAL 104 teaches

    Module 104 is about using deployments to separate workflow code from execution
    infrastructure. The workshop covers work pools, managed infrastructure, Docker,
    Git-based code storage, and why teams use deployment templates as guardrails.
- type: text
  contents: |-
    # Local adaptation

    Instead of depending on Prefect Cloud, this lab uses a local process work pool so
    you can still practice the same mental model: define a flow, package it from a
    source location, create a deployment, and inspect it in the UI.
tabs:
- id: iepwocw3wfm5
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: p6zv1iekggjo
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: bszyjgyza6xh
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
# Create Local Deployments

This challenge adapts PAL 104 into a local process deployment workflow.

## Step 1: Create a flow to deploy

Create `/root/pal/local_deploy.py` with a flow named `greet_flow` that:

- uses `@flow(log_prints=True)`
- accepts a `name` parameter
- prints a greeting and the current file path

## Step 2: Create a deployment launcher

Create `/root/pal/deploy_local.py` that:

- imports `Path`
- loads `greet_flow` from local source using `.from_source(...)`
- creates a deployment with `.deploy(...)`
- uses `work_pool_name="pal-process-pool"`
- names the deployment `pal-local-greeting`

Use the local directory as the source path.

## Step 3: Build the deployment

Run:

```run
cd /root/pal
uv run deploy_local.py
prefect deployment ls
```

You should see a deployment named `pal-local-greeting`.

## Step 4: Connect back to PAL

The workshop also compares managed, Docker, and Git-based deployment patterns. Those
options change where code runs and how it is packaged, but the deployment object still
serves the same purpose: a reusable, schedulable definition of how a flow should run.

## Verify

Before clicking **Check**, make sure:

- `local_deploy.py` defines `greet_flow`
- `deploy_local.py` uses `.from_source(` and `.deploy(`
- the deployment targets `pal-process-pool`
- `prefect deployment ls` shows `pal-local-greeting`
