---
slug: state-management-across-interactions
id: lynpsi0osnl2
type: challenge
title: Remember One Selection
teaser: Save one clicked project in MCP state.
notes:
- type: text
  contents: |-
    # Tiny state

    Context state is what lets one interaction influence the next one. Without it, every tool call would have to start from scratch.

    This final challenge uses that idea in the smallest possible way: one clicked project gets saved, and the next view uses that saved value to decide what to show.

    The important lesson is that state gives your app continuity. A user should not have to repeat the same selection every time they click a different tool, and MCP context gives you a simple way to remember that choice across interactions.
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
  path: /root/project-dashboard
difficulty: basic
timelimit: 900
enhanced_loading: null
---
# Remember One Selection

This last step ties the course together. One tool records a choice in MCP state, and another tool reads it back so the app can keep its place between interactions. That pattern is what makes multi-step app experiences feel connected instead of isolated.

The behavior is tiny, but the idea is important: the app should remember what the learner just selected without making them start over. You are wiring that memory into the server in two directions, first by saving the choice and then by reading it back when the details view opens.

Open `project_dashboard/server.py`.

The first tool is the write path, and the second tool is the read path. Keeping them separate makes it easier to see how state moves through the app, and it mirrors how many real MCP apps coordinate multiple small interactions.

Update `remember_selected_project` so it saves the clicked project id with:

```python
await ctx.set_state("selected_project_id", project_id)
```

Update `selected_project_details` so it reads the saved id with `await ctx.get_state("selected_project_id")`.

That read is what lets the details view stay in sync with the previous click. If the state lookup fails or returns nothing, the app should fall back to the prompt telling the learner to pick a project.

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

With the dev server running, click one project in the browser and then open the details view. The selection should carry across the interaction instead of resetting to the default prompt.

## Verify

In App Preview, click one project and open its details. The detail view should match the project you clicked, which confirms the app remembered your selection between tool calls.
