from __future__ import annotations

import json

from fastmcp import Context, FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, LineChart, Metric

from project_dashboard.helpers import load_metrics


mcp = FastMCP("Project Dashboard")


@mcp.resource("dashboard://metrics")
def dashboard_metrics_resource() -> dict:
    return load_metrics()


@mcp.tool(app=True)
async def delivery_metrics_dashboard(ctx: Context) -> PrefabApp:
    metrics = json.loads((await ctx.read_resource("dashboard://metrics"))[0].text)

    with Column(gap=2, cssClass="p-6") as view:
        Heading("Delivery Metrics")
        Metric("Velocity", metrics["summary"]["velocity"])
        LineChart(metrics["trend"])
    return PrefabApp(title="Delivery Metrics", view=view)


if __name__ == "__main__":
    mcp.run()
