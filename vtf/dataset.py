"""Deterministic dataset generation and JSONL persistence."""

import json
from dataclasses import dataclass
from pathlib import Path

from vtf.questions.templates import generate_task_batch
from vtf.schemas import Task


@dataclass(frozen=True)
class DatasetBundle:
    """Kept tasks and rejection accounting for a generation run."""

    tasks: list[Task]
    rejected: list[Task]
    rejection_stats: dict[str, int]


def generate_dataset(n: int, *, seed: int = 7) -> DatasetBundle:
    """Generate a balanced task set with deterministic accounting."""

    tasks = generate_task_batch(n, seed=seed)
    return DatasetBundle(
        tasks=tasks,
        rejected=[],
        rejection_stats={"generated": len(tasks), "kept": len(tasks), "rejected": 0},
    )


def write_tasks_jsonl(tasks: list[Task], output_path: Path) -> None:
    """Write task records as UTF-8 JSON Lines."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for task in tasks:
            handle.write(json.dumps(task.model_dump(mode="json"), sort_keys=True) + "\n")
