"""
Weekly task batches loaded from tasks.json.
Each week has exactly 6 tasks. Tasks are specific and actionable.
"""

import json
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_tasks_file = os.path.join(_dir, "tasks.json")

with open(_tasks_file, "r") as f:
    _data = json.load(f)

WEEKLY_TASKS: dict[int, list[str]] = {
    int(k): v for k, v in _data["weekly_tasks"].items()
}

MAINTENANCE_TASKS: list[str] = _data["maintenance_tasks"]


def get_tasks_for_week(week_number: int) -> list[str]:
    """Return the 6 tasks for a given week number."""
    if week_number in WEEKLY_TASKS:
        return WEEKLY_TASKS[week_number]
    return MAINTENANCE_TASKS
