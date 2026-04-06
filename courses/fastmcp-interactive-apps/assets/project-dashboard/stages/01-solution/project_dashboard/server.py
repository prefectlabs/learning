from __future__ import annotations

from fastmcp import FastMCP
from prefab_ui.app import PrefabApp
from prefab_ui.components import Badge, Column, Heading, Row, Text

from project_dashboard.helpers import (
    bug_priority_variant,
    load_bugs,
    load_projects,
    project_status_label,
    project_status_variant,
)


mcp = FastMCP("Project Dashboard")


@mcp.tool(app=True)
def project_status_board() -> PrefabApp:
    """Render the current project board as a Prefab app."""
    with Column(gap=6, cssClass="p-6") as view:
        Heading("Project Status Board")
        Text("Scan the delivery board without leaving the conversation.")

        for project in load_projects():
            with Column(gap=2, cssClass="rounded-lg border p-4"):
                with Row(gap=2, justify="between", align="center"):
                    Heading(project["name"], level=3)
                    Badge(
                        project_status_label(project["status"]),
                        variant=project_status_variant(project["status"]),
                    )
                Text(f"Owner: {project['owner']}")
                Text(f"Sprint: {project['sprint']}")
                Text(f"Focus: {project['focus']}")
                Text(f"Completion: {project['completion']}%")

    return PrefabApp(title="Project Status Board", view=view)


@mcp.tool(app=True)
def bug_backlog_card() -> PrefabApp:
    """Render the bug backlog as a visual card list."""
    with Column(gap=6, cssClass="p-6") as view:
        Heading("Bug Backlog")
        Text("Keep the highest-priority issues visible while you build.")

        for bug in load_bugs():
            with Column(gap=2, cssClass="rounded-lg border p-4"):
                with Row(gap=2, justify="between", align="center"):
                    Heading(bug["id"], level=3)
                    Badge(bug["priority"], variant=bug_priority_variant(bug["priority"]))
                Text(bug["title"])
                Text(f"Team: {bug['team']}")
                Text(f"Status: {bug['status']}")

    return PrefabApp(title="Bug Backlog", view=view)


if __name__ == "__main__":
    mcp.run()
