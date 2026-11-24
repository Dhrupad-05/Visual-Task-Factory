from vtf.render.effects import apply_effects
from vtf.scene.generator import generate_scene


def test_effects_are_seeded_and_preserve_dimensions() -> None:
    scene = generate_scene(seed=4, chart_type="bar", n_series=1, n_points=3)
    pixels = bytes([100, 120, 140, 255]) * (8 * 6)

    first = apply_effects(pixels, width=8, height=6, noise="light", seed=21)
    second = apply_effects(pixels, width=8, height=6, noise="light", seed=21)

    assert first == second
    assert len(first) == len(pixels)
    assert scene.style.noise == "none"
