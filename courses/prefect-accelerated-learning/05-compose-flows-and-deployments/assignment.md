---
slug: compose-flows-and-deployments
id: rywzz2qg9fpz
type: challenge
title: Compose Flows and Deployments
teaser: Practice nested flows and deployment chaining using PAL's workflow design
  patterns.
notes:
- type: text
  contents: |-
    # What PAL 105 is about

    Module 105 introduces workflow pattern archetypes: monoflows, subflows, flows of
    deployments, and event-driven workflows. The goal is not to memorize patterns, but
    to understand when extra structure helps with organization, infrastructure control,
    and state visibility.
- type: text
  contents: |-
    # What you'll build locally

    This lab focuses on two patterns from the slides: nested flows and running a
    deployment from another flow. They are enough to show how Prefect composes work at
    different levels without needing a cloud-only setup.
tabs:
- id: tz6cwwnqw67j
  title: Terminal
  type: terminal
  hostname: prefect-sandbox
  cmd: /bin/bash
- id: 3uhgwue5rgk7
  title: Code Editor
  type: code
  hostname: prefect-sandbox
  path: /root/pal
- id: dzrbftcbygpq
  title: Prefect UI
  type: browser
  hostname: local-prefect-server
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
# Compose Flows and Deployments

This challenge adapts PAL 105's composition patterns.

## Step 1: Create a nested-flow example

Create `/root/pal/animal_facts.py` with:

- a flow named `fetch_cat_fact`
- a flow named `fetch_dog_fact`
- a parent flow named `animal_facts`

Use `httpx` to fetch one cat fact and one dog fact, then print both from the parent
flow.

## Step 2: Trigger a deployment from a flow

Create `/root/pal/run_local_deployment.py` with a flow named `run_local_deployment`
that calls:

```python
run_deployment(name="greet-flow/pal-local-greeting", parameters={"name": "Prefect"})
```

If your deployment name uses a different flow slug, adjust the left side of the name to
match what Prefect created in the previous challenge. The key skill is using
`run_deployment(...)` inside a flow.

## Step 3: Run the nested flow

Execute:

```run
cd /root/pal
uv run animal_facts.py
```

## Step 4: Review the design tradeoff

PAL 105 also covers custom events and deployment triggers. In practice, nested flows
help organize related work, while deployment chaining becomes useful once the child run
needs its own schedule, infrastructure, or lifecycle.

## Verify

Before clicking **Check**, make sure:

- `animal_facts.py` contains three `@flow` definitions
- `run_local_deployment.py` imports and uses `run_deployment`
- the deployment name references `pal-local-greeting`
