---
slug: forms-and-user-input
id: gqqawuwe9bmx
type: challenge
title: Build Forms and User Input Workflows
teaser: Use FastMCPApp and manual Prefab forms to collect a bug report and refresh
  the backlog.
notes:
- type: text
  contents: |-
    # When to move past `app=True`

    `@mcp.tool(app=True)` is perfect for display-first experiences. But once your UI needs its own entry point plus backend-only helper tools, `FastMCPApp` gives you a cleaner structure.

    That's the shift you'll make here: one UI entry tool, one backend mutation tool, and a form that connects them with `CallTool`.
- type: text
  contents: |-
    # Manual form focus

    This challenge intentionally uses a **manual** Prefab form rather than a generated Pydantic form. That gives you hands-on practice with:

    - `Form`
    - `Input`
    - `Textarea`
    - `Select`
    - `SelectOption`
    - `Button`
tabs:
- id: 4eo66rfgsf71
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- id: opla1ui3pdxh
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root
- id: ywfmmupankwr
  title: App Preview
  type: browser
  hostname: fastmcp-app-preview
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
Build forms and user input workflows
===

Your dashboard now renders visually. Next, you'll add a real workflow: collecting a bug report and updating the backlog from the UI.

## Step 1: Review the FastMCPApp scaffold

Open `project_dashboard/server.py` and find:

- `dashboard_app = FastMCPApp("Dashboard")`
- `bug_report_workflow`
- `submit_bug_report`

The scaffolding is there, but the UI is still a placeholder.

## Step 2: Build the manual form

Replace the placeholder UI in `bug_report_workflow` with a manual form that includes:

- a text input for the bug title
- a team selector
- a priority selector
- a multiline description field
- a submit button

Use `Form(onSubmit=CallTool(...))` to wire the submit action to `submit_bug_report`.

## Step 3: Process the submission

Update `submit_bug_report` so it:

1. loads the current bug list
2. appends a new bug
3. saves the updated backlog
4. returns a confirmation message and the refreshed bug list

Then use `SetState`, `ShowToast`, and the returned result so the UI shows:

- a confirmation card
- an updated backlog list

## Step 4: Preview the workflow

Run the dev server again:

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

Open **App Preview**, launch the bug intake workflow, and submit a sample bug.

## Verify

Before you click **Check**, confirm:

- `bug_report_workflow` is registered with `@dashboard_app.ui()`
- `submit_bug_report` is registered with `@dashboard_app.tool()`
- submitting the form updates `project_dashboard/data/bugs.json`
- the UI shows a confirmation message and refreshed backlog content
