"""Canvas, visibility, and occlusion evidence checks."""

from itertools import product

from vtf.render.boxes import PixelBox
from vtf.validate.result import ValidationResult


def _inside(box: PixelBox, width: int, height: int) -> bool:
    return (
        0 <= box.x0 <= box.x1 <= width
        and 0 <= box.y0 <= box.y1 <= height
        and box.x1 > box.x0
        and box.y1 > box.y0
    )


def _intersection_area(left: PixelBox, right: PixelBox) -> float:
    width = max(0.0, min(left.x1, right.x1) - max(left.x0, right.x0))
    height = max(0.0, min(left.y1, right.y1) - max(left.y0, right.y0))
    return width * height


def validate_evidence(
    boxes: dict[str, list[PixelBox]],
    *,
    width: int,
    height: int,
    required_groups: tuple[str, ...],
    occluded_pairs: tuple[tuple[str, str], ...] = (),
    max_occlusion: float = 0.2,
) -> ValidationResult:
    """Ensure required boxes are visible, in-canvas, and not mostly covered."""

    if width <= 0 or height <= 0:
        raise ValueError("canvas dimensions must be positive")
    if not 0 <= max_occlusion <= 1:
        raise ValueError("max_occlusion must be between zero and one")
    for group in required_groups:
        if not boxes.get(group):
            return ValidationResult.reject("missing_evidence", group=group)
        for box in boxes[group]:
            if not _inside(box, width, height):
                return ValidationResult.reject("box_out_of_canvas", group=group, box=box)
    for target_group, occluder_group in occluded_pairs:
        for target, occluder in product(boxes.get(target_group, []), boxes.get(occluder_group, [])):
            target_area = (target.x1 - target.x0) * (target.y1 - target.y0)
            if target_area <= 0:
                return ValidationResult.reject("occluded_element", group=target_group)
            ratio = _intersection_area(target, occluder) / target_area
            if ratio > max_occlusion:
                return ValidationResult.reject(
                    "occluded_element", group=target_group, occlusion=ratio
                )
    return ValidationResult.ok()
