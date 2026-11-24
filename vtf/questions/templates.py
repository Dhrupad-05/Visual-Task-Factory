"""Deterministic question templates for the six required skills."""

from pathlib import Path

from vtf.questions.answers import (
    answer_crossing_x,
    answer_exaggerates_change,
    answer_highest_series,
    answer_legend_series,
    answer_percent_change,
    answer_reading,
    answer_truncated,
)
from vtf.questions.misconceptions import compute_distractors
from vtf.schemas import SceneSpec, Task


def _task(
    scene: SceneSpec,
    *,
    skill: str,
    subskill: str,
    question: str,
    answer_type: str,
    reference_answer: object,
    choices: list[str] | None = None,
    tolerance: float | None = None,
    difficulty: dict[str, object] | None = None,
) -> Task:
    """Build a Task and attach its spec-derived distractors."""

    task = Task(
        task_id=f"{scene.id}-{skill}",
        image_path=Path(f"data/images/{scene.id}.png"),
        scene_id=scene.id,
        skill=skill,
        subskill=subskill,
        question=question,
        answer_type=answer_type,  # type: ignore[arg-type]
        choices=choices,
        reference_answer=reference_answer,
        tolerance=tolerance,
        difficulty=difficulty or {},
        severity_params={"trap_type": subskill, "scale": 1.0},
    )
    return task.model_copy(update={"distractors": compute_distractors(scene, task)})


def generate_tasks(scene: SceneSpec) -> list[Task]:
    """Generate one deterministic task for each of the six skill categories."""

    panel = scene.panels[0]
    first_series = panel.series[0]
    point_index = 0
    last_point = len(first_series.values) - 1
    highest = answer_highest_series(scene, point_index=point_index)
    colors = [series.color for series in panel.series]
    tasks = [
        _task(
            scene,
            skill="reading",
            subskill="exact_value",
            question=f"What is the value of {first_series.name} at {panel.x_labels[point_index]}?",
            answer_type="numeric",
            reference_answer=answer_reading(scene, series_index=0, point_index=point_index),
            tolerance=0.01,
            difficulty={"panel_index": 0, "series_index": 0, "point_index": point_index},
        ),
        _task(
            scene,
            skill="comparison",
            subskill="highest_at_x",
            question=f"Which series is highest at {panel.x_labels[point_index]}?",
            answer_type="choice",
            reference_answer=highest,
            choices=[series.name for series in panel.series],
            difficulty={"panel_index": 0, "series_index": 0, "point_index": point_index},
        ),
        _task(
            scene,
            skill="relational",
            subskill="legend_mapping",
            question=f"Which series does color {colors[0]} represent?",
            answer_type="choice",
            reference_answer=answer_legend_series(scene, series_index=0),
            choices=[series.name for series in panel.series],
            difficulty={"panel_index": 0, "series_index": 0, "point_index": point_index},
        ),
        _task(
            scene,
            skill="multi_step",
            subskill="percent_change",
            question=f"By what percent did {first_series.name} change from {panel.x_labels[0]} to {panel.x_labels[-1]}?",
            answer_type="numeric",
            reference_answer=answer_percent_change(
                scene, series_index=0, first_point=0, last_point=last_point
            ),
            tolerance=0.01,
            difficulty={"panel_index": 0, "series_index": 0, "first_point": 0, "last_point": last_point},
        ),
        _task(
            scene,
            skill="trap_detection",
            subskill="truncated_axis",
            question="Is the vertical axis truncated?",
            answer_type="yes_no",
            reference_answer=answer_truncated(scene),
            difficulty={"panel_index": 0},
        ),
        _task(
            scene,
            skill="robustness",
            subskill="exaggerated_change",
            question="Does this chart make the change look larger than it is?",
            answer_type="yes_no",
            reference_answer=answer_exaggerates_change(scene),
            difficulty={"panel_index": 0, "clutter_level": scene.style.clutter_level},
        ),
    ]
    return tasks


def generate_task_batch(n: int, *, seed: int = 7) -> list[Task]:
    """Generate a deterministic batch by cycling chart types and skill templates."""

    if n < 1:
        raise ValueError("n must be positive")
    from vtf.scene.generator import generate_scene

    tasks: list[Task] = []
    chart_types = ["bar", "line", "scatter"]
    scene_index = 0
    while len(tasks) < n:
        scene = generate_scene(
            seed=seed + scene_index,
            chart_type=chart_types[scene_index % len(chart_types)],
            n_series=2 + scene_index % 3,
            n_points=3 + scene_index % 4,
        )
        tasks.extend(generate_tasks(scene))
        scene_index += 1
    return tasks[:n]
