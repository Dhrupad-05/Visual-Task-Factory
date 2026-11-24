"""Severity-weighted model rankings and sensitivity checks."""

from numbers import Real

from vtf.schemas import Task


def _severity(task: Task, predicted: object, *, numeric_scale: float, distractor_penalty: float) -> float:
    if predicted == task.reference_answer:
        return 0.0
    if task.answer_type == "numeric" and isinstance(task.reference_answer, Real) and isinstance(predicted, Real):
        truth = float(task.reference_answer)
        error = 1.0 if truth == 0 else abs(float(predicted) - truth) / abs(truth)
        return min(1.0, error * numeric_scale)
    if any(predicted == distractor for distractor in task.distractors.values()):
        return distractor_penalty
    return 1.0


def rank_models(
    cases_by_model: dict[str, list[tuple[Task, object]]],
    *,
    numeric_scale: float = 1.0,
    distractor_penalty: float = 1.5,
) -> list[tuple[str, float]]:
    """Rank models by one-minus-mean severity under explicit constants."""

    if numeric_scale <= 0 or distractor_penalty <= 0:
        raise ValueError("severity constants must be positive")
    scores = {
        model: 1.0
        - sum(
            _severity(task, predicted, numeric_scale=numeric_scale, distractor_penalty=distractor_penalty)
            for task, predicted in cases
        )
        / len(cases)
        for model, cases in cases_by_model.items()
        if cases
    }
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
