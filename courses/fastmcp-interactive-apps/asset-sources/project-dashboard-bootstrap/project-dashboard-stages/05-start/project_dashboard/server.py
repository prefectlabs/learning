from __future__ import annotations

from fastmcp import Context, FastMCP
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import Button, Column, Heading, Text

from project_dashboard.helpers import find_project, load_projects


mcp = FastMCP("Project Dashboard")


@mcp.tool(app=True)
async def project_browser() -> PrefabApp:
    with Column(gap=2, cssClass="p-6") as view:
        Heading("Project Browser")
        Text("Pick one project.")
        for project in load_projects():
            Button(
                project["name"],
                onClick=CallTool(
                    "remember_selected_project",
                    arguments={"project_id": project["id"]},
                    onSuccess=CallTool("selected_project_details"),
                ),
            )
    return PrefabApp(title="Project Browser", view=view)


@mcp.tool
async def remember_selected_project(ctx: Context, project_id: str) -> dict:
    await ctx.set_state("selected_project_id", project_id)
    return {"project_id": project_id}


@mcp.tool(app=True)
async def selected_project_details(ctx: Context) -> PrefabApp:
    project_id = await ctx.get_state("selected_project_id")
    project = find_project(project_id) if project_id else None

    with Column(gap=2, cssClass="p-6") as view:
        Heading("Selected Project")
        if project is None:
            Text("Pick a project.")
        else:
            Heading(project["name"], level=2)
            Text(f"Status: {project['status']}")
    return PrefabApp(title="Selected Project", view=view)


if __name__ == "__main__":
    mcp.run()
