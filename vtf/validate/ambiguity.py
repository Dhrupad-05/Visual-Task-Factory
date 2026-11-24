"""Choice ambiguity and rounding-boundary checks."""

from vtf.validate.result import ValidationResult


def validate_choice_margin(
    *, top: float, second: float, value_range: float, threshold: float = 0.05
) -> ValidationResult:
    """Reject choices whose top-two margin is below a fraction of the range."""

    if value_range <= 0:
        raise ValueError("value_range must be positive")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    margin_ratio = abs(top - second) / value_range
    if margin_ratio < threshold:
        return ValidationResult.reject(
            "ambiguous_choice", margin_ratio=margin_ratio, threshold=threshold
        )
    return ValidationResult.ok(margin_ratio=margin_ratio)
