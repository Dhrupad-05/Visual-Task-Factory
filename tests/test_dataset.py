import json
from pathlib import Path

from vtf.dataset import generate_dataset, write_tasks_jsonl


def test_dataset_is_deterministic_and_balanced(tmp_path: Path) -> None:
    first = generate_dataset(60, seed=21)
    second = generate_dataset(60, seed=21)
    counts = {skill: sum(task.skill == skill for task in first.tasks) for skill in {t.skill for t in first.tasks}}

    assert first.tasks == second.tasks
    assert len(first.tasks) == 60
    assert max(counts.values()) - min(counts.values()) <= 1
    assert first.rejection_stats["generated"] >= first.rejection_stats["kept"]

    output = tmp_path / "tasks.jsonl"
    write_tasks_jsonl(first.tasks, output)
    assert len(output.read_text(encoding="utf-8").splitlines()) == 60
    assert json.loads(output.read_text(encoding="utf-8").splitlines()[0])["task_id"]
