"""Reference-answer versus rendered-value checks."""

from numbers import Real
import math
from typing import Any

from vtf.schemas import Task
from vtf.validate.result import ValidationResult


def recover_axis_value(
    *,
    pixel_y: float,
    plot_top: float,
    plot_bottom: float,
    y_min: float,
    y_max: float,
    y_type: str = "linear",
) -> float:
    """Recover a value from a pixel y-coordinate and calibrated plot bounds."""

    if plot_bottom <= plot_top:
        raise ValueError("plot_bottom must be greater than plot_top")
    if y_max <= y_min:
        raise ValueError("y_max must be greater than y_min")
    fraction = (pixel_y - plot_top) / (plot_bottom - plot_top)
    if y_type == "linear":
        return y_max - fraction * (y_max - y_min)
    if y_type == "log":
        if y_min <= 0 or y_max <= 0:
            raise ValueError("log axes require positive bounds")
        return 10 ** (math.log10(y_max) - fraction * (math.log10(y_max) - math.log10(y_min)))
    raise ValueError(f"unsupported axis type: {y_type}")


def validate_reextraction(task: Task, *, extracted_answer: Any) -> ValidationResult:
    """Check a pixel-recovered answer against the task reference."""

    truth = task.reference_answer
    tolerance = task.tolerance or 0.0
    if isinstance(truth, Real) and not isinstance(truth, bool) and isinstance(extracted_answer, Real):
        error = abs(float(extracted_answer) - float(truth))
        if error <= tolerance:
            return ValidationResult.ok(error=error)
        return ValidationResult.reject("reference_mismatch", error=error, tolerance=tolerance)
    if extracted_answer == truth:
        return ValidationResult.ok(error=0)
    return ValidationResult.reject("reference_mismatch", extracted=extracted_answer, truth=truth)
