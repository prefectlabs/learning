from __future__ import annotations

from fastmcp import FastMCP, FastMCPApp
from prefab_ui.actions import SetState
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import Button, Column, Form, Heading, If, Input, Text


mcp = FastMCP("Project Dashboard")
dashboard_app = FastMCPApp("Dashboard")


@dashboard_app.ui()
def bug_report_workflow() -> PrefabApp:
    with Column(gap=2, cssClass="p-6") as view:
        Heading("Bug Report")
        Text("Send one bug title.")

        with Form(
            onSubmit=CallTool(
                submit_bug_report,
                arguments={"title": "{{ title }}"},
                onSuccess=[SetState("saved", True)],
            )
        ):
            Input(name="title", placeholder="Webhook retries")
            Button("Save", buttonType="submit")

        with If("saved"):
            Text("Saved.")

    return PrefabApp(title="Bug Report", view=view, state={"saved": False})


@dashboard_app.tool()
def submit_bug_report(title: str) -> dict:
    return {"message": "Saved."}


mcp.add_provider(dashboard_app)


if __name__ == "__main__":
    mcp.run()
