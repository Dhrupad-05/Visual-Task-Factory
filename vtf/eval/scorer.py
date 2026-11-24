"""Type-aware parsing and scoring."""

import re
from dataclasses import dataclass
from numbers import Real

from vtf.schemas import Task


@dataclass(frozen=True)
class ScoreResult:
    """Parsed prediction and scoring outcome."""

    correct: bool
    format_failure: bool
    parsed: object | None
    raw_text: str


def parse_numeric(raw_text: str) -> float | None:
    """Parse common numeric answer forms, including commas, currency, and k/m suffixes."""

    match = re.search(r"[-+]?\$?\d[\d,]*(?:\.\d+)?\s*[kKmMbB]?%?", raw_text)
    if not match:
        return None
    token = match.group(0).replace(",", "").replace("$", "").strip()
    multiplier = 1.0
    if token[-1:].lower() in {"k", "m", "b"}:
        multiplier = {"k": 1_000.0, "m": 1_000_000.0, "b": 1_000_000_000.0}[token[-1].lower()]
        token = token[:-1].strip()
    token = token.rstrip("%").strip()
    return float(token) * multiplier


def _normalize(raw_text: str) -> str:
    answer = re.split(r"answer:\s*", raw_text, maxsplit=1, flags=re.IGNORECASE)[-1]
    return re.sub(r"[^a-z0-9]+", " ", answer.lower()).strip()


def _parse_yes_no(raw_text: str) -> bool | None:
    normalized = _normalize(raw_text)
    if normalized.startswith("yes") or normalized == "true":
        return True
    if normalized.startswith("no") or normalized == "false":
        return False
    return None


def score_task(task: Task, raw_text: str) -> ScoreResult:
    """Score one raw answer according to its declared answer type."""

    if task.answer_type == "numeric":
        parsed = parse_numeric(raw_text)
        if parsed is None:
            return ScoreResult(False, True, None, raw_text)
        truth = float(task.reference_answer)
        correct = abs(parsed - truth) <= (task.tolerance or 0.0)
        return ScoreResult(correct, False, parsed, raw_text)
    if task.answer_type == "yes_no":
        parsed = _parse_yes_no(raw_text)
        return ScoreResult(parsed is not None and parsed == task.reference_answer, parsed is None, parsed, raw_text)
    if task.answer_type == "choice":
        parsed = _normalize(raw_text)
        if not parsed:
            return ScoreResult(False, True, None, raw_text)
        return ScoreResult(parsed == _normalize(str(task.reference_answer)), False, parsed, raw_text)
    if task.answer_type == "set":
        parsed = {_normalize(item) for item in raw_text.split(",") if item.strip()}
        truth = {_normalize(str(item)) for item in task.reference_answer}
        return ScoreResult(bool(parsed) and parsed == truth, not bool(parsed), parsed, raw_text)
    parsed = raw_text.strip()
    return ScoreResult(bool(parsed) and parsed == str(task.reference_answer), not bool(parsed), parsed, raw_text)
