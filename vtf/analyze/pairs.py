"""Minimal-pair accuracy and flip-rate summaries."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PairOutcome:
    """Correctness for both members of one controlled pair."""

    pair_id: str
    factor: str
    base_correct: bool
    variant_correct: bool


@dataclass(frozen=True)
class PairSummary:
    """Aggregated pair metrics."""

    pairs: int
    flip_rate: float
    accuracy_delta: float


def analyze_pairs(outcomes: list[PairOutcome]) -> dict[str, PairSummary]:
    """Compute flip rate and variant-minus-base accuracy by factor."""

    grouped: dict[str, list[PairOutcome]] = {}
    for outcome in outcomes:
        grouped.setdefault(outcome.factor, []).append(outcome)
    summaries: dict[str, PairSummary] = {}
    for factor, group in grouped.items():
        flips = sum(item.base_correct != item.variant_correct for item in group)
        delta = sum(item.variant_correct for item in group) / len(group) - sum(
            item.base_correct for item in group
        ) / len(group)
        summaries[factor] = PairSummary(len(group), flips / len(group), delta)
    return summaries
