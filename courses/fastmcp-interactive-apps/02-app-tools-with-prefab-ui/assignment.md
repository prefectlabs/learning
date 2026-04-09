---
slug: app-tools-with-prefab-ui
id: b3m6pfcfwxyc
type: challenge
title: Turn Tools into Tiny Apps
teaser: Make two tools show UI.
notes:
- type: text
  contents: |-
    # Tiny app tools

    A regular MCP tool usually returns text or data. When you mark a tool with `app=True`, it can return a Prefab UI view instead, which makes the tool feel like a small interactive screen instead of a plain response.

    In this challenge, you will do that twice. The point is not to build two different designs. The point is to see that the same pattern works for more than one tool, so the UI behavior becomes something you can reuse.

    This is the first place where the course starts to feel like an app instead of a single demo. You will keep working in the same file, but now the file defines more than one entry point into the UI. That is a useful mental model for FastMCP apps, because one server can expose several small experiences at once.
tabs:
- id: xu2hw12vnd88
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- id: ksn6gywggqas
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root/project-dashboard
difficulty: basic
timelimit: 900
enhanced_loading: null
---
## Turn Two Tools into Tiny Apps

You already have two tools in the same file. Now you will give each tool a tiny UI so the preview opens a card instead of plain text. This is a good checkpoint for understanding how `app=True` changes the return type and how `PrefabApp` wraps the view you build.

The code stays small, but the idea grows a little: the tool is no longer just returning a value, it is returning a view. That is why the imports and the decorator change together. If those two pieces do not line up, the preview will not know how to render the tool.

Open `project_dashboard/server.py`.

Start by adding the UI imports at the top of the file. You are preparing the module to build a view, not changing the tool logic yet, so this step is mostly about teaching the file which components it can use.

Add these imports:

```python
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text
```

Once the imports are in place, update each tool one at a time. Keep the first card as a small status-style view and the second as a second card, so you can see that the pattern works more than once without introducing any extra layout complexity.

Change `project_status_board` and `bug_backlog_card` so each one:

1. uses `@mcp.tool(app=True)`
2. returns a `PrefabApp`
3. shows a tiny card with `Heading` and `Text`

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

Run the app after both tools are updated so you can compare the two cards side by side in the preview. If one tool still shows plain text, that usually means its decorator or return type was missed.

## Verify

In App Preview, both tools should show a small card instead of plain text, with the tool titles still visible. That tells you the app is now rendering UI for multiple tools from the same file.
