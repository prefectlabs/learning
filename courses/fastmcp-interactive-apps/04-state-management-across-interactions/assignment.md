---
slug: state-management-across-interactions
id: lynpsi0osnl2
type: challenge
title: Persist State Across Interactions
teaser: Store selections in the MCP context so one tool call can drive the next.
notes:
- type: text
  contents: |-
    # Why MCP context state matters

    Interactive apps rarely end after one click. A user might choose a filter, select an item, and then ask for more detail. To make that feel continuous, the server needs to remember what happened earlier in the same MCP session.

    FastMCP's `Context` gives you that session-aware state through `get_state` and `set_state`.
- type: text
  contents: |-
    # Goal for this challenge

    You'll build a three-part flow:

    1. show a filtered project browser
    2. remember which project the user selected
    3. render a detail card from that saved selection

    The important part is that the selection survives across tool invocations.
tabs:
- id: am88rkdsxulr
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- id: 4xux4t4vsoz6
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root
- id: a792svgxtkn2
  title: App Preview
  type: browser
  hostname: fastmcp-app-preview
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
Persist state across interactions
===

In this final challenge, you'll make the dashboard feel like a multi-step app instead of a collection of isolated tool calls.

## Step 1: Persist the active filter

Update `remember_board_filter` so it stores the selected filter with:

```python
await ctx.set_state("active_board_filter", ...)
```

Then update `project_browser` so it reads that value with `await ctx.get_state(...)` and only shows the matching projects.

## Step 2: Persist the selected project

Update `remember_selected_project` so it stores:

```python
await ctx.set_state("selected_project_id", project_id)
```

Then wire the browser buttons so choosing a project saves the selection before opening the detail tool.

## Step 3: Render the detail view from state

Update `selected_project_details` so it reads the saved project id from the MCP context, loads the matching project, and renders a proper detail card.

Also show the active filter somewhere in the detail view so you can confirm both pieces of state are working.

## Step 4: Preview the workflow

Run the preview server:

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

Open **App Preview** and test the sequence:

1. open `project_browser`
2. set a filter
3. choose a project
4. open the detail tool

## Verify

Before you click **Check**, confirm:

- the browser persists the active filter with `ctx.set_state`
- the selection persists with `ctx.set_state`
- the detail tool reads the saved selection with `ctx.get_state`
- the selected project details match the project you clicked
