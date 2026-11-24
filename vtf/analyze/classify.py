"""Misconception classification against stored distractor answers."""

from dataclasses import dataclass
import re
from numbers import Real

from vtf.eval.scorer import score_task
from vtf.schemas import Task


@dataclass(frozen=True)
class Classification:
    """One prediction's failure label."""

    label: str
    parsed: object | None


def _normalize(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def classify_prediction(task: Task, raw_text: str) -> Classification:
    """Label correct, format-failure, misconception, ambiguous, or other."""

    scored = score_task(task, raw_text)
    if scored.format_failure:
        return Classification("format_failure", None)
    if scored.correct:
        return Classification("correct", scored.parsed)
    parsed = scored.parsed
    tolerance = task.tolerance or 0.0
    matches: list[str] = []
    for label, distractor in task.distractors.items():
        if isinstance(parsed, Real) and not isinstance(parsed, bool) and isinstance(distractor, Real):
            matches.append(label) if abs(float(parsed) - float(distractor)) <= tolerance else None
        elif _normalize(parsed) == _normalize(distractor):
            matches.append(label)
    if len(matches) == 1:
        return Classification(matches[0], parsed)
    if len(matches) > 1:
        return Classification("ambiguous", parsed)
    return Classification("other", parsed)
