---
slug: app-tools-with-prefab-ui
id: b3m6pfcfwxyc
type: challenge
title: Render App Tools with Prefab UI
teaser: Convert text-only tools into visual app tools with Prefab components and local
  preview.
notes:
- type: text
  contents: |-
    # Why app tools matter

    Standard MCP tools are great for text output, but dashboards, scorecards, and status boards are easier to understand when the tool can render structure directly in the conversation.

    In FastMCP, the easiest way to start is to keep your existing tool and add `app=True`. Once you do that, the tool can return a `PrefabApp` instead of plain text.
- type: text
  contents: |-
    # What you'll practice

    In this challenge, you'll take the existing `Project Dashboard` starter and upgrade two tools:

    - `project_status_board`
    - `bug_backlog_card`

    You'll use Prefab layout primitives like `Heading`, `Text`, `Badge`, `Row`, and `Column`, then preview the result locally with `fastmcp dev apps`.
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
  path: /root
- id: gpfqgubflnvb
  title: App Preview
  type: browser
  hostname: fastmcp-app-preview
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
Render app tools with Prefab UI
===

In this challenge, you'll convert the starter dashboard from plain strings into visual app responses.

## Step 1: Open the starter project

Move into the workspace and activate the environment that was prepared for you:

```run
cd /root/project-dashboard
source .venv/bin/activate
pwd
ls
```

Open `project_dashboard/server.py`. Right now both dashboard tools return strings, which means the preview can only show plain text.

## Step 2: Convert the tools into app tools

Update `project_status_board` and `bug_backlog_card` so they:

1. Use `@mcp.tool(app=True)`
2. Return `PrefabApp`
3. Render structured content with:
   - `Heading`
   - `Text`
   - `Badge`
   - `Row`
   - `Column`

Keep the same project and bug data from the helper functions. The goal is to turn the same information into a visual status board.

## Step 3: Preview the app locally

Start the FastMCP app dev server:

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

Then open the **App Preview** tab. You should be able to select your tools and see the rendered UI.

## Verify

Before you click **Check**, confirm:

- `project_status_board` returns a `PrefabApp`
- `bug_backlog_card` returns a `PrefabApp`
- both tools use `@mcp.tool(app=True)`
- the preview shows headings, badges, and grouped rows/columns instead of plain text
