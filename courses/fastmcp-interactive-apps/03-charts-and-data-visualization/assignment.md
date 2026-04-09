---
slug: charts-and-data-visualization
id: eycd6to13yyy
type: challenge
title: Show One Tiny Chart
teaser: Turn resource data into a small chart.
notes:
- type: text
  contents: |-
    # Tiny charts

    Resources are useful when you want to separate the data from the UI that displays it. In this stage, the resource still provides the project metrics, but the app tool turns that data into a visual summary.

    You will only draw one metric and one trend line. That is enough to show the pattern: read resource data, convert it into Python objects, and then hand those objects to Prefab UI components.

    The key thing to notice is that the resource and the chart solve different problems. The resource is the data contract; the chart is the presentation layer. Keeping those pieces separate makes the app easier to extend later, because you can change the visualization without changing where the data comes from.
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
  path: /root/project-dashboard
difficulty: basic
timelimit: 900
enhanced_loading: null
---
# Show One Tiny Chart

This challenge connects the MCP resource layer to the app layer. Instead of hard-coding values into the UI, you will load the metrics resource and use its data to render a small dashboard view. That is the key move behind a lot of useful MCP apps: data comes from one place, the presentation comes from another.

The app already knows where the metrics live, so your job is to turn that stored data into something the user can read quickly. The chart should still stay tiny. One metric and one line chart are enough to show that the data is flowing through the app correctly.

Open `project_dashboard/server.py`.

Before you touch the tool, make sure you leave the resource definition in place. The challenge is about consuming the resource, not rewriting it. That separation matters because later tools can reuse the same resource without duplicating the source data.

Keep the `dashboard://metrics` resource.

Then add the imports the tool needs for parsing JSON and rendering the chart. These imports are doing two jobs at once: one converts the resource text into structured data, and the others turn that data into a UI the preview can display.

Add these imports:

```python
import json
from fastmcp import Context
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, LineChart, Metric
```

Use this line to turn the resource into data:

```python
metrics = json.loads((await ctx.read_resource("dashboard://metrics"))[0].text)
```

That single line is the bridge between the resource and the visualization. `ctx.read_resource` gives you the raw resource content, and `json.loads` turns it into a Python object that the components can read.

Change `delivery_metrics_dashboard` so it:

1. uses `@mcp.tool(app=True)`
2. reads the resource with `await ctx.read_resource("dashboard://metrics")`
3. uses `json.loads` to get the data
4. shows one `Metric` for velocity
5. shows one `LineChart` for the trend

```run
cd /root/project-dashboard
source .venv/bin/activate
fastmcp dev apps project_dashboard/server.py
```

Once the app is running, check that the chart is driven by the resource values rather than hard-coded numbers. If the preview looks empty, the usual place to inspect is the JSON parsing step or the resource read call.

## Verify

In App Preview, the tool should open a small chart view with one metric and one line chart, and the velocity value should reflect the metrics resource. That confirms the UI is reading live resource data instead of static placeholders.
