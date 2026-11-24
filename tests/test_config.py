from vtf.config import Settings


def test_settings_have_reproducible_defaults() -> None:
    first = Settings()
    second = Settings()

    assert first.seed == second.seed == 7
    assert first.image_width > 0
    assert first.image_height > 0
    assert first.matplotlib_backend == "Agg"
