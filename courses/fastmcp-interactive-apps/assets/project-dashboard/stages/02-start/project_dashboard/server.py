from __future__ import annotations

from fastmcp import FastMCP, FastMCPApp
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
dashboard_app = FastMCPApp("Dashboard")


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


@dashboard_app.ui()
def bug_report_workflow() -> PrefabApp:
    """Open the bug intake workflow."""
    with Column(gap=6, cssClass="p-6") as view:
        Heading("Bug Report Intake")
        Text("Replace this placeholder with a manual form that calls submit_bug_report.")
        Text("You will add text inputs, dropdowns, and a confirmation card in this challenge.")

    return PrefabApp(
        title="Bug Report Intake",
        view=view,
        state={
            "submitted": False,
            "confirmation_message": "",
            "bugs": load_bugs(),
        },
    )


@dashboard_app.tool()
def submit_bug_report(title: str, team: str, priority: str, description: str) -> dict:
    """Create a new bug report and return the updated backlog."""
    return {
        "message": "TODO: save the bug and return the updated backlog.",
        "bugs": load_bugs(),
        "title": title,
        "team": team,
        "priority": priority,
        "description": description,
    }


mcp.add_provider(dashboard_app)


if __name__ == "__main__":
    mcp.run()
