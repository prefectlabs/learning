from __future__ import annotations

from fastmcp import FastMCP

from project_dashboard.helpers import load_bugs, load_projects


mcp = FastMCP("Project Dashboard")


@mcp.tool
def project_status_board() -> str:
    """Summarize the current project board."""
    projects = load_projects()
    lines = ["Project Status Board"]
    for project in projects:
        lines.append(
            f"- {project['name']}: {project['status']} | owner={project['owner']} | "
            f"sprint={project['sprint']} | completion={project['completion']}%"
        )
    return "\n".join(lines)


@mcp.tool
def bug_backlog_card() -> str:
    """Show a compact bug backlog summary."""
    bugs = load_bugs()
    lines = ["Bug Backlog"]
    for bug in bugs:
        lines.append(f"- {bug['id']}: {bug['title']} ({bug['priority']})")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
