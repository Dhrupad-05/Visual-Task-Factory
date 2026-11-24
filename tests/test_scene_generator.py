from vtf.scene.generator import generate_scene


def test_generator_is_identical_for_the_same_seed() -> None:
    first = generate_scene(seed=11, chart_type="line", n_series=3, n_points=4)
    second = generate_scene(seed=11, chart_type="line", n_series=3, n_points=4)

    assert first == second


def test_generator_respects_knob_ranges() -> None:
    scene = generate_scene(seed=3, chart_type="scatter", n_series=4, n_points=7)

    assert scene.knobs["n_series"] == 4
    assert scene.knobs["n_points"] == 7
    assert len(scene.panels) == 1
    assert len(scene.panels[0].series) == 4
    assert all(len(series.values) == 7 for series in scene.panels[0].series)
