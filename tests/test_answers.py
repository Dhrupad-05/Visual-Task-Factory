from vtf.questions.answers import (
    answer_crossing_x,
    answer_highest_series,
    answer_percent_change,
    answer_reading,
    answer_truncated,
    misconception_log_read_as_linear,
)
from vtf.schemas import AxisSpec, PanelSpec, SceneSpec, SeriesSpec


def _hand_scene() -> SceneSpec:
    return SceneSpec(
        id="hand",
        seed=1,
        chart_type="line",
        panels=[
            PanelSpec(
                axes=AxisSpec(x_type="numeric", y_type="linear", y_min=0, y_max=200),
                series=[
                    SeriesSpec(name="A", color="red", values=[100, 150, 200]),
                    SeriesSpec(name="B", color="blue", values=[200, 150, 100]),
                ],
                x_labels=["0", "1", "2"],
            )
        ],
    )


def test_hand_computed_reading_and_percent_change() -> None:
    scene = _hand_scene()
    # Hand computation: A at index 1 is 150; (150 - 100) / 100 * 100 = 50%.
    assert answer_reading(scene, series_index=0, point_index=1) == 150
    assert answer_percent_change(scene, series_index=0, first_point=0, last_point=1) == 50


def test_hand_computed_crossing_and_truncation() -> None:
    scene = _hand_scene()
    # Hand computation: A-B changes from -100 to 0, so the first crossing is x=1.
    assert answer_crossing_x(scene, first_series=0, second_series=1) == 1.0
    assert answer_truncated(scene) is False


def test_tied_comparison_uses_first_series_deterministically() -> None:
    scene = _hand_scene()
    # Hand computation: A and B are both 150 at index 1; stable input order
    # makes A the deterministic answer rather than inventing a tie-break.
    assert answer_highest_series(scene, point_index=1) == "A"


def test_hand_computed_log_axis_linear_misread() -> None:
    scene = _hand_scene()
    scene.panels[0].axes = AxisSpec(x_type="numeric", y_type="log", y_min=1, y_max=100)
    scene.panels[0].series[0].values = [10]
    # Hand computation: 10 is halfway from log10(1)=0 to log10(100)=2;
    # a linear read maps that halfway position to (1 + 100) / 2 = 50.5.
    assert misconception_log_read_as_linear(scene, series_index=0, point_index=0) == 50.5
