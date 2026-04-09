from __future__ import annotations

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text


mcp = FastMCP("Project Dashboard")


@mcp.tool(app=True)
def project_status_board() -> PrefabApp:
    with Column(gap=2, cssClass="p-6") as view:
        Heading("API Revamp")
        Text("On track.")
    return PrefabApp(title="Project Status", view=view)


@mcp.tool(app=True)
def bug_backlog_card() -> PrefabApp:
    with Column(gap=2, cssClass="p-6") as view:
        Heading("Bugs")
        Text("Webhook retries.")
    return PrefabApp(title="Bug Backlog", view=view)


if __name__ == "__main__":
    mcp.run()
