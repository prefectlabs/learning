from __future__ import annotations

import json

from fastmcp import Context, FastMCP, FastMCPApp
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Button,
    Column,
    ForEach,
    Form,
    Heading,
    If,
    Input,
    Metric,
    Row,
    Select,
    SelectOption,
    Text,
    Textarea,
)
from prefab_ui.components.charts import BarChart, ChartSeries, LineChart

from project_dashboard.helpers import (
    bug_priority_variant,
    load_bugs,
    load_metrics,
    load_projects,
    next_bug_id,
    project_status_label,
    project_status_variant,
    save_bugs,
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
        Text("Collect a structured bug report and refresh the backlog in place.")

        with Form(
            gap=4,
            onSubmit=CallTool(
                submit_bug_report,
                arguments={
                    "title": "{{ title }}",
                    "team": "{{ team }}",
                    "priority": "{{ priority }}",
                    "description": "{{ description }}",
                },
                onSuccess=[
                    SetState("submitted", True),
                    SetState("confirmation_message", "{{ $result.message }}"),
                    SetState("bugs", "{{ $result.bugs }}"),
                    ShowToast("Bug report saved", variant="success"),
                ],
            ),
        ):
            Text("Bug title")
            Input(
                name="title",
                placeholder="Login form stops responding after refresh",
                required=True,
            )

            Text("Team")
            with Select(name="team", placeholder="Choose a team", required=True):
                SelectOption("API Revamp", value="API Revamp")
                SelectOption("Mobile Beta", value="Mobile Beta")
                SelectOption("Analytics Hub", value="Analytics Hub")

            Text("Priority")
            with Select(name="priority", placeholder="Choose a priority", required=True):
                SelectOption("P1", value="P1")
                SelectOption("P2", value="P2")
                SelectOption("P3", value="P3")

            Text("Description")
            Textarea(
                name="description",
                rows=4,
                placeholder="Describe what the user did, what happened, and what you expected instead.",
                required=True,
            )

            Button("Submit bug report", buttonType="submit")

        with If("submitted"):
            with Column(gap=2, cssClass="rounded-lg border p-4"):
                Badge("Saved", variant="success")
                Text("{{ confirmation_message }}")

        Heading("Updated backlog", level=2)
        with ForEach("bugs"):
            with Column(gap=2, cssClass="rounded-lg border p-4"):
                with Row(gap=2, justify="between", align="center"):
                    Text("{{ $item.id }}")
                    Badge("{{ $item.priority }}", variant="outline")
                Text("{{ $item.title }}")
                Text("{{ $item.team }}")
                Text("{{ $item.status }}")

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
    bugs = load_bugs()
    new_bug = {
        "id": next_bug_id(bugs),
        "title": title,
        "team": team,
        "priority": priority,
        "description": description,
        "status": "triage",
    }
    bugs.append(new_bug)
    save_bugs(bugs)
    return {
        "message": f"Created {new_bug['id']} for {team}.",
        "bugs": bugs,
    }


@mcp.resource("dashboard://metrics")
def dashboard_metrics_resource() -> dict:
    """Expose project metrics through a resource."""
    return load_metrics()


@mcp.tool(app=True)
async def delivery_metrics_dashboard(ctx: Context) -> PrefabApp:
    """Render delivery charts from resource-backed metrics."""
    resource_result = await ctx.read_resource("dashboard://metrics")
    metrics = json.loads(resource_result.contents[0].content)
    summary = metrics["summary"]

    with Column(gap=6, cssClass="p-6") as view:
        Heading("Delivery Metrics")
        Text("Read the metrics resource, then visualize it in the conversation.")

        with Row(gap=4):
            Metric(
                label="Velocity",
                value=summary["velocity"],
                description="Story points closed this sprint",
            )
            Metric(
                label="Reliability",
                value=f"{summary['reliability']}%",
                description="Successful workflow runs",
            )
            Metric(
                label="Open incidents",
                value=summary["open_incidents"],
                description="Critical items still active",
            )

        LineChart(
            data=metrics["delivery_trend"],
            series=[
                ChartSeries(dataKey="planned", label="Planned"),
                ChartSeries(dataKey="completed", label="Completed"),
            ],
            xAxis="week",
            showDots=True,
        )

        BarChart(
            data=metrics["project_health"],
            series=[
                ChartSeries(dataKey="throughput", label="Throughput"),
                ChartSeries(dataKey="bugs", label="Open Bugs"),
            ],
            xAxis="project",
        )

    return PrefabApp(title="Delivery Metrics", view=view)


mcp.add_provider(dashboard_app)


if __name__ == "__main__":
    mcp.run()
