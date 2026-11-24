"""Minimal-pair integrity validation."""

from typing import Any

from vtf.scene.pairs import ScenePair
from vtf.validate.result import ValidationResult


def _diff_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        paths: list[str] = []
        for key in set(left) | set(right):
            paths.extend(_diff_paths(left.get(key), right.get(key), f"{path}.{key}"))
        return paths
    if isinstance(left, list) and isinstance(right, list):
        paths: list[str] = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            paths.extend(_diff_paths(left_item, right_item, f"{path}[{index}]"))
        if len(left) != len(right):
            paths.append(path)
        return [path] if paths and path.endswith(".style.palette") else paths
    return [] if left == right else [path]


_EXPECTED_PATHS = {
    "axis_type": ".panels[0].axes.y_type",
    "baseline": ".panels[0].axes.y_min",
    "color_similarity": ".style.palette",
    "dual_axis": ".panels[0].axes.dual_axis",
    "font_size": ".style.font_size",
}


def validate_pair(pair: ScenePair) -> ValidationResult:
    """Require exactly the declared scene-spec field to differ."""

    expected = _EXPECTED_PATHS.get(pair.factor_changed)
    if expected is None:
        raise ValueError(f"unsupported pair factor: {pair.factor_changed}")
    paths = _diff_paths(pair.base.model_dump(), pair.variant.model_dump())
    if paths != [expected]:
        return ValidationResult.reject(
            "pair_two_factors" if len(paths) > 1 else "pair_wrong_factor",
            changed_paths=paths,
            expected_path=expected,
        )
    return ValidationResult.ok(changed_path=expected)
