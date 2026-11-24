"""Duplicate-task detection."""

import re

from vtf.schemas import Task


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def duplicate_task_ids(tasks: list[Task]) -> dict[str, str]:
    """Return duplicate task id -> first task id mappings."""

    seen: dict[tuple[str, str], str] = {}
    duplicates: dict[str, str] = {}
    for task in tasks:
        key = (task.scene_id, _normalize(task.question))
        if key in seen:
            duplicates[task.task_id] = seen[key]
        else:
            seen[key] = task.task_id
    return duplicates
