from vtf.scene.generator import generate_scene
from vtf.scene.pairs import make_pair
from vtf.validate.pairs import validate_pair


def test_pair_two_factors_fixture_is_rejected() -> None:
    scene = generate_scene(seed=18, chart_type="line", n_series=2, n_points=3)
    pair = make_pair(scene, factor="axis_type", pair_id="pair-18")
    pair.variant.style.font_size += 2

    result = validate_pair(pair)

    assert not result.passed
    assert result.reason == "pair_two_factors"


def test_good_pair_fixture_passes() -> None:
    scene = generate_scene(seed=19, chart_type="bar", n_series=2, n_points=3)
    pair = make_pair(scene, factor="baseline", pair_id="pair-19")

    assert validate_pair(pair).passed
