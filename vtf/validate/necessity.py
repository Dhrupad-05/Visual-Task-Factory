"""Heuristic image-necessity checks used before text-only baselines."""

import re

from vtf.schemas import Task
from vtf.validate.result import ValidationResult


def _answer_text(task: Task) -> str:
    """Return a normalized representation for answer-presence checks."""

    answer = task.reference_answer
    if isinstance(answer, bool):
        return "yes" if answer else "no"
    if isinstance(answer, float) and answer.is_integer():
        return str(int(answer))
    return str(answer)


def validate_image_necessity(task: Task) -> ValidationResult:
    """Flag questions that literally reveal their own reference answer."""

    answer = _answer_text(task)
    if re.search(rf"(?<![\w.]){re.escape(answer)}(?![\w.])", task.question, re.IGNORECASE):
        return ValidationResult.reject("text_answerable", answer=answer)
    return ValidationResult.ok()
