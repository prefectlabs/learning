---
slug: intro-mcp-apps
id: plujb0vvbsg0
type: challenge
title: Make Your First MCP App
teaser: Make one tiny MCP app.
notes:
- type: text
  contents: |-
    # MCP apps

    MCP apps let a tool return a UI instead of plain text. That changes the experience from reading output in a terminal to opening a small view inside the app preview.

    This first challenge keeps the example tiny on purpose: one heading and one sentence. The goal is to show the loop you will use throughout the track, where you edit one tool, preview the result, and confirm the UI matches what you expected.

    As you work, watch for the split between code and experience. The code lives in `project_dashboard/server.py`, but the payoff shows up in the App Preview tab. That pattern repeats in every later challenge, so it is worth noticing now.
tabs:
- id: muebfucy90qa
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- id: xurq1rd0y60w
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root/project-dashboard
- id: rcc7ov7yjdsx
  title: App Preview
  type: service
  hostname: fastmcp-sandbox
  port: 8080
difficulty: basic
timelimit: 600
enhanced_loading: null
---
# Make a Tiny MCP App

This first edit shows the simplest possible FastMCP app: one tool, one UI view, and one visible change in the preview. You are not building a full dashboard yet. You are just proving that an app tool can render something structured.

The important part is not the wording in the app. It is the shape of the interaction: edit one small function, start the dev server, and watch the UI update in place. Once that feels familiar, the later challenges will feel like small variations on the same loop.

Open `project_dashboard/server.py`.

You only need to change one line, so use the file as a map of the app rather than a place to refactor. The preview should stay open while you edit, because the point of the exercise is to see the UI respond as soon as the app reloads.

Change the text under the heading to `This is my first MCP app.`.

That single sentence is enough to prove the UI is wired correctly. Keep the heading as-is so you can compare the old and new state without changing the rest of the view.

Preview it with:

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

The dev server keeps the feedback loop short: save the file, let FastMCP reload, and check the App Preview tab. If the text does not update, that usually means the app process is still starting or the file change has not been saved yet.

## Verify

In App Preview, you should see one heading and one short sentence, with the sentence changed to `This is my first MCP app.`. That confirms the app is returning UI instead of plain text.
<!-- ![](../assets/project-dashboard-bootstrap.tar.gz) -->
