"""Spec-derived misconception answers and collision filtering."""

from typing import Any

from vtf.questions.answers import (
    answer_percent_change,
    answer_reading,
    misconception_log_read_as_linear,
)
from vtf.schemas import SceneSpec, Task


def _close(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= tolerance
    return left == right


def filter_distractors(truth: Any, candidates: dict[str, Any], tolerance: float) -> dict[str, Any]:
    """Drop distractors indistinguishable from truth or earlier distractors."""

    retained: dict[str, Any] = {}
    for name, candidate in candidates.items():
        if _close(candidate, truth, tolerance):
            continue
        if any(_close(candidate, prior, tolerance) for prior in retained.values()):
            continue
        retained[name] = candidate
    return retained


def compute_distractors(scene: SceneSpec, task: Task) -> dict[str, Any]:
    """Compute applicable misconception answers for a generated task."""

    params = task.difficulty
    panel_index = int(params.get("panel_index", 0))
    series_index = int(params.get("series_index", 0))
    point_index = int(params.get("point_index", 0))
    candidates: dict[str, Any] = {}
    numeric = task.answer_type == "numeric"
    if numeric and task.subskill == "exact_value" and scene.panels[panel_index].axes.y_type == "log":
        candidates["log_read_as_linear"] = misconception_log_read_as_linear(
            scene, series_index=series_index, point_index=point_index, panel_index=panel_index
        )
    if len(scene.panels[panel_index].series) > 1 and (numeric or task.answer_type == "choice"):
        other_index = (series_index + 1) % len(scene.panels[panel_index].series)
        if numeric:
            candidates["wrong_series"] = answer_reading(
                scene, series_index=other_index, point_index=point_index, panel_index=panel_index
            )
        else:
            candidates["wrong_series"] = next(
                series.name
                for series in scene.panels[panel_index].series
                if series.name != task.reference_answer
            )
    if numeric and task.subskill == "exact_value":
        value = answer_reading(scene, series_index=series_index, point_index=point_index, panel_index=panel_index)
        candidates["off_by_tick"] = value + 1
    if task.subskill == "percent_change":
        first_point = int(params["first_point"])
        last_point = int(params["last_point"])
        axis_min = scene.panels[panel_index].axes.y_min
        first = answer_reading(scene, series_index=series_index, point_index=first_point, panel_index=panel_index)
        last = answer_reading(scene, series_index=series_index, point_index=last_point, panel_index=panel_index)
        if axis_min > 0:
            candidates["truncated_baseline_ignored"] = (last - axis_min) / (first - axis_min) * 100
        candidates["wrong_series"] = answer_percent_change(
            scene, series_index=(series_index + 1) % len(scene.panels[panel_index].series),
            first_point=first_point, last_point=last_point, panel_index=panel_index,
        )
    tolerance = task.tolerance if task.tolerance is not None else 0.01
    return filter_distractors(task.reference_answer, candidates, tolerance)
