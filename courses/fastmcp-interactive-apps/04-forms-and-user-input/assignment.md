---
slug: forms-and-user-input
id: gqqawuwe9bmx
type: challenge
title: Make a Simple Form
teaser: Send one value from a form to a tool.
notes:
- type: text
  contents: |-
    # One form

    Forms let a learner send structured input to a tool without leaving the app view. That matters because interactive apps are not just for display. They can also collect one choice or one short piece of text and pass it into your backend logic.

    Here, the form is intentionally tiny: one input, one button, and one success message. That keeps the focus on the submission flow and on the state change that happens after the tool runs.

    You are also seeing a more realistic pattern than the earlier challenges. The UI collects input, the backend tool handles the work, and the view updates only after the submit succeeds. That separation is what makes the form feel interactive instead of decorative.
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
  path: /root/project-dashboard
difficulty: basic
timelimit: 900
enhanced_loading: null
---
# Make a Simple Form

This challenge shows the round trip from a UI form to a backend tool and back to a visible success state. You are not building a full workflow engine. You are showing that a fast, small interaction can still collect input, call a tool, and update the screen.

The pattern here is useful because it splits responsibility cleanly. The form gathers data, `submit_bug_report` handles the backend action, and the UI state flips to show the learner what happened. Once you understand that loop, it becomes much easier to build richer app flows.

Open `project_dashboard/server.py`.

Keep the backend tool exactly where it is so the exercise stays focused on the UI workflow. The interesting part is how the form triggers the tool and how the UI reacts after the tool succeeds.

Keep `submit_bug_report` as the backend tool.

Then trim `bug_report_workflow` down to the smallest meaningful form. One input is enough to prove the submission path, and one button is enough to trigger it, so there is no need to add validation or extra fields yet.

Make `bug_report_workflow` tiny:

1. keep `@dashboard_app.ui()`
2. use one `Input`
3. use one `Button`
4. show `Saved.` after a successful submit

Use `Form(onSubmit=CallTool(...))` and `SetState("saved", True)`.

That combination is what gives the learner a visible success state. The submit action calls the tool, and the state update lets the view reveal `Saved.` after the action completes.

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

After the dev server is running, submit a short bug title in the preview and watch for the success message to appear. If the message does not show up, the likely issue is that the state update or submit handler is not wired to the form.

## Verify

In App Preview, submit one bug title and see `Saved.` appear after the form runs. That confirms the user input made it through the tool and the UI responded to the result.
