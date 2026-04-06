---
slug: charts-and-data-visualization
id: eycd6to13yyy
type: challenge
title: Visualize Resource Data with Charts
teaser: Read dashboard metrics through a resource and render chart components inside
  the conversation.
notes:
- type: text
  contents: |-
    # Tools plus resources

    This challenge introduces a useful pattern:

    1. expose structured data through a resource
    2. read that resource from a tool with `ctx.read_resource(...)`
    3. render the result as an app

    That separation keeps the data contract explicit while still letting the tool decide how to present it.
- type: text
  contents: |-
    # Chart components in Prefab

    Prefab includes interactive chart components that render directly in the conversation. In this lab you'll use:

    - `Metric`
    - `LineChart`
    - `BarChart`
    - `ChartSeries`
tabs:
- id: 7ti5mgxmxqod
  title: "\U0001F4BB Terminal"
  type: terminal
  hostname: fastmcp-sandbox
  cmd: /bin/bash
- id: evpgsdggsvez
  title: "\U0001F6A7 Code Editor"
  type: code
  hostname: fastmcp-sandbox
  path: /root
- id: esxenq4vbu9y
  title: App Preview
  type: browser
  hostname: fastmcp-app-preview
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---
Visualize resource data with charts
===

Your dashboard can render layouts and handle form submissions. Now you'll add a metrics view that reads real data through a FastMCP resource and turns it into charts.

## Step 1: Add the metrics resource

Open `project_dashboard/server.py` and add a resource with this URI:

```python
@mcp.resource("dashboard://metrics")
```

The resource should return the data from `load_metrics()`.

## Step 2: Upgrade the metrics tool

Right now `delivery_metrics_dashboard` only returns a string summary. Replace it with an app tool that:

1. accepts `ctx: Context`
2. reads the resource with `await ctx.read_resource("dashboard://metrics")`
3. parses the resource contents
4. renders:
   - summary metrics with `Metric`
   - a `LineChart`
   - a `BarChart`

Use the fixture data in `project_dashboard/data/metrics.json`.

## Step 3: Preview the dashboard

Run the preview server:

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

Then open **App Preview** and launch the metrics tool.

## Verify

Before you click **Check**, confirm:

- the resource URI is exactly `dashboard://metrics`
- `delivery_metrics_dashboard` uses `@mcp.tool(app=True)`
- the tool reads metrics through `ctx.read_resource(...)`
- the rendered output includes chart components, not just text
