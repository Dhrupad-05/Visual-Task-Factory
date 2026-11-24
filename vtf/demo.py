"""Small cached demo workflow for local rehearsal."""

import asyncio
import json
from pathlib import Path
from dataclasses import dataclass

from vtf.eval.adapters import MockModelAdapter
from vtf.eval.cache import DiskCache
from vtf.eval.runner import EvaluationRunner
from vtf.questions.templates import generate_tasks
from vtf.render.charts import render_scene
from vtf.scene.generator import generate_scene


@dataclass(frozen=True)
class DemoResult:
    """Demo execution counts."""

    task_count: int
    api_calls: int
    cache_hits: int
    output_path: Path


def run_demo(output_dir: Path, *, n: int = 5, model_name: str = "mock") -> DemoResult:
    """Generate, render, score, and cache a small deterministic demo run."""

    if n < 1:
        raise ValueError("n must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    image_dir = output_dir / "images"
    tasks = []
    scene_index = 0
    while len(tasks) < n:
        scene = generate_scene(seed=7 + scene_index, chart_type=("bar", "line", "scatter")[scene_index % 3])
        image_path = image_dir / f"{scene.id}.png"
        render_scene(scene, image_path)
        tasks.extend(task.model_copy(update={"image_path": image_path}) for task in generate_tasks(scene))
        scene_index += 1
    tasks = tasks[:n]
    adapter = MockModelAdapter(responses=[str(task.reference_answer) for task in tasks])
    runner = EvaluationRunner(
        adapter=adapter,
        model_name=model_name,
        cache=DiskCache(output_dir / "cache"),
    )
    result = asyncio.run(runner.evaluate(tasks))
    output_path = output_dir / "demo.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for task, score in zip(tasks, result.scores):
            handle.write(
                json.dumps(
                    {"task_id": task.task_id, "question": task.question, "answer": score.raw_text, "correct": score.correct}
                )
                + "\n"
            )
    return DemoResult(len(tasks), result.api_calls, result.cache_hits, output_path)
