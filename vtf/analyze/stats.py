"""Accuracy estimates and difficulty degradation summaries."""

from dataclasses import dataclass
import math

from vtf.eval.scorer import ScoreResult
from vtf.schemas import Task


@dataclass(frozen=True)
class AccuracySummary:
    """Count, accuracy, and Wilson confidence interval for a group."""

    correct: int
    total: int
    accuracy: float
    ci_low: float
    ci_high: float


def wilson_interval(correct: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Return a Wilson score interval for a binomial proportion."""

    if total <= 0 or not 0 <= correct <= total or z <= 0:
        raise ValueError("invalid binomial counts or z")
    proportion = correct / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def _summary(scores: list[ScoreResult]) -> AccuracySummary:
    total = len(scores)
    if total == 0:
        raise ValueError("cannot summarize an empty group")
    correct = sum(score.correct for score in scores)
    low, high = wilson_interval(correct, total)
    return AccuracySummary(correct, total, correct / total, low, high)


def accuracy_by_knob(
    tasks: list[Task], scores: list[ScoreResult], *, knob: str
) -> dict[str, AccuracySummary]:
    """Group aligned task scores by a stored difficulty knob."""

    if len(tasks) != len(scores):
        raise ValueError("tasks and scores must be aligned")
    grouped: dict[str, list[ScoreResult]] = {}
    for task, score in zip(tasks, scores):
        if knob not in task.difficulty:
            raise KeyError(f"task {task.task_id} lacks difficulty knob {knob}")
        grouped.setdefault(str(task.difficulty[knob]), []).append(score)
    return {level: _summary(group) for level, group in sorted(grouped.items())}
