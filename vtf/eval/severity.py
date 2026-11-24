"""Decision-impact severity scoring."""

from numbers import Real

from vtf.schemas import Task


def severity_score(task: Task, predicted: object) -> float:
    """Return capped error severity, with distractor matches weighted higher."""

    truth = task.reference_answer
    if predicted == truth:
        return 0.0
    if task.answer_type == "numeric" and isinstance(truth, Real) and isinstance(predicted, Real):
        truth_float = float(truth)
        if truth_float == 0:
            return 1.0
        return min(1.0, abs(float(predicted) - truth_float) / abs(truth_float))
    if any(predicted == distractor for distractor in task.distractors.values()):
        return 1.5
    return 1.0


def decision_weighted_accuracy(severities: list[float]) -> float:
    """Convert mean severity to a score where 1 is perfect."""

    if not severities:
        raise ValueError("severities must not be empty")
    return 1.0 - sum(severities) / len(severities)
