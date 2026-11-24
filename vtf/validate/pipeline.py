"""Orchestration for the independent task validators."""

from vtf.render.boxes import PixelBox
from vtf.schemas import Task
from vtf.validate.ambiguity import validate_choice_margin
from vtf.validate.evidence import validate_evidence
from vtf.validate.necessity import validate_image_necessity
from vtf.validate.reextract import validate_reextraction
from vtf.validate.result import ValidationResult


def validate_task(
    task: Task,
    *,
    extracted_answer: object,
    evidence: dict[str, list[PixelBox]] | None = None,
    canvas: tuple[int, int] | None = None,
    required_evidence: tuple[str, ...] = (),
    occluded_pairs: tuple[tuple[str, str], ...] = (),
    choice_values: tuple[float, float, float] | None = None,
) -> ValidationResult:
    """Run available validators in deterministic order and return first failure."""

    checks = [validate_reextraction(task, extracted_answer=extracted_answer)]
    if choice_values is not None:
        top, second, value_range = choice_values
        checks.append(validate_choice_margin(top=top, second=second, value_range=value_range))
    if evidence is not None:
        if canvas is None:
            raise ValueError("canvas is required when evidence is provided")
        checks.append(
            validate_evidence(
                evidence,
                width=canvas[0],
                height=canvas[1],
                required_groups=required_evidence,
                occluded_pairs=occluded_pairs,
            )
        )
    checks.append(validate_image_necessity(task))
    return next((check for check in checks if not check.passed), ValidationResult.ok())
