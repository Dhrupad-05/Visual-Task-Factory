from vtf.scene.generator import generate_scene
from vtf.scene.pairs import make_pair


def _diff_paths(left: object, right: object, path: str = "") -> list[str]:
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
        if paths and path.endswith(".style.palette"):
            return [path]
        return paths
    return [] if left == right else [path]


def test_pair_changes_only_axis_type_and_keeps_data() -> None:
    base = generate_scene(seed=9, chart_type="line", n_series=2, n_points=4)
    original_values = base.panels[0].series[0].values

    pair = make_pair(base, factor="axis_type", pair_id="pair-9")
    diff = _diff_paths(pair.base.model_dump(), pair.variant.model_dump())

    assert pair.base.id == base.id
    assert pair.pair_id == "pair-9"
    assert pair.factor_changed == "axis_type"
    assert diff == [".panels[0].axes.y_type"]
    assert pair.variant.panels[0].series[0].values == original_values


def test_pair_changes_color_factor_only_in_visual_fields() -> None:
    base = generate_scene(seed=10, chart_type="bar", n_series=2, n_points=3)
    pair = make_pair(base, factor="color_similarity", pair_id="pair-10")
    diff = _diff_paths(pair.base.model_dump(), pair.variant.model_dump())

    assert pair.factor_changed == "color_similarity"
    assert diff == [".style.palette"]
