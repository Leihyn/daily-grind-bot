"""
Persistence layer for tracking task completion.
State file lives in the repo — GitHub Actions commits it after each run.
"""

import json
import os
from datetime import datetime, date

from config import STATE_FILE, START_DATE


DEFAULT_STATE = {
    "start_date": START_DATE,
    "completed": {},  # {"week_number": [task_indices]}
    "seen_issues": [],  # GitHub issue URLs already notified about
    "notify_index": 0,  # Which notification slot we're on (0-5) for round-robin
}


def _ensure_dir():
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)


def load_state() -> dict:
    _ensure_dir()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_STATE.copy()


def save_state(state: dict):
    _ensure_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_current_week() -> int:
    """Calculate current week number based on start date."""
    state = load_state()
    start = datetime.strptime(state["start_date"], "%Y-%m-%d").date()
    today = date.today()
    days_elapsed = (today - start).days
    week = (days_elapsed // 7) + 1
    return max(1, week)


def get_completed_tasks(week: int) -> list[int]:
    """Get list of completed task indices (0-based) for a week."""
    state = load_state()
    return state["completed"].get(str(week), [])


def mark_task_done(week: int, task_index: int) -> bool:
    """Mark a task as done. Returns True if it was newly completed."""
    state = load_state()
    week_key = str(week)
    if week_key not in state["completed"]:
        state["completed"][week_key] = []
    if task_index not in state["completed"][week_key]:
        state["completed"][week_key].append(task_index)
        save_state(state)
        return True
    return False


def get_incomplete_tasks(week: int, all_tasks: list[str]) -> list[tuple[int, str]]:
    """Return list of (index, task_text) for incomplete tasks."""
    completed = get_completed_tasks(week)
    return [(i, t) for i, t in enumerate(all_tasks) if i not in completed]


def all_tasks_complete(week: int, total_tasks: int) -> bool:
    """Check if all tasks for a week are done."""
    completed = get_completed_tasks(week)
    return len(completed) >= total_tasks


def add_seen_issue(url: str):
    state = load_state()
    if url not in state["seen_issues"]:
        state["seen_issues"].append(url)
        # Keep only last 200 to prevent unbounded growth
        state["seen_issues"] = state["seen_issues"][-200:]
        save_state(state)


def is_issue_seen(url: str) -> bool:
    state = load_state()
    return url in state["seen_issues"]


def get_and_advance_notify_index() -> int:
    """Get current notify slot (0-5) and advance for next call."""
    state = load_state()
    idx = state.get("notify_index", 0)
    state["notify_index"] = (idx + 1) % 6
    save_state(state)
    return idx
