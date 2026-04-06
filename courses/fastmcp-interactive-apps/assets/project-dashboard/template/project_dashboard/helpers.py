from __future__ import annotations

import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parent
DATA_ROOT = PACKAGE_ROOT / "data"


def _read_json(name: str):
    return json.loads((DATA_ROOT / name).read_text())


def _write_json(name: str, payload) -> None:
    (DATA_ROOT / name).write_text(json.dumps(payload, indent=2) + "\n")


def load_projects() -> list[dict]:
    return _read_json("projects.json")


def load_bugs() -> list[dict]:
    return _read_json("bugs.json")


def save_bugs(bugs: list[dict]) -> None:
    _write_json("bugs.json", bugs)


def load_metrics() -> dict:
    return _read_json("metrics.json")


def next_bug_id(bugs: list[dict]) -> str:
    current = 0
    for bug in bugs:
        bug_id = bug["id"].split("-")[-1]
        current = max(current, int(bug_id))
    return f"BUG-{current + 1:03d}"


def project_status_label(status: str) -> str:
    if status == "all":
        return "All"
    return status.replace("-", " ").title()


def project_status_variant(status: str) -> str:
    return {
        "on-track": "success",
        "at-risk": "warning",
        "blocked": "destructive",
    }.get(status, "secondary")


def bug_priority_variant(priority: str) -> str:
    return {
        "P1": "destructive",
        "P2": "warning",
        "P3": "info",
    }.get(priority, "secondary")


def find_project(project_id: str) -> dict | None:
    for project in load_projects():
        if project["id"] == project_id:
            return project
    return None


def filter_projects(board_filter: str) -> list[dict]:
    projects = load_projects()
    if board_filter == "all":
        return projects
    return [project for project in projects if project["status"] == board_filter]
