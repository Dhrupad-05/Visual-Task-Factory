"""Seeded synthetic chart scene generation."""

import random

from vtf.schemas import AxisSpec, PanelSpec, SceneSpec, SeriesSpec, StyleSpec


_PALETTE = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6"]


def generate_scene(
    *,
    seed: int,
    chart_type: str = "bar",
    n_series: int = 2,
    n_points: int = 5,
) -> SceneSpec:
    """Generate one deterministic scene from a seed and bounded knobs."""

    if chart_type not in {"bar", "line", "scatter"}:
        raise ValueError("chart_type must be bar, line, or scatter")
    if not 1 <= n_series <= len(_PALETTE):
        raise ValueError(f"n_series must be between 1 and {len(_PALETTE)}")
    if not 1 <= n_points <= 50:
        raise ValueError("n_points must be between 1 and 50")
    rng = random.Random(seed)
    values_by_series = [
        [round(rng.uniform(2.0, 100.0), 2) for _ in range(n_points)]
        for _ in range(n_series)
    ]
    maximum = max(value for values in values_by_series for value in values)
    series = [
        SeriesSpec(
            name=f"Series {index + 1}",
            color=_PALETTE[index],
            marker="o",
            values=values,
        )
        for index, values in enumerate(values_by_series)
    ]
    return SceneSpec(
        id=f"scene-{seed}",
        seed=seed,
        chart_type=chart_type,  # type: ignore[arg-type]
        panels=[
            PanelSpec(
                axes=AxisSpec(x_type="categorical", y_type="linear", y_min=1, y_max=maximum * 1.2),
                series=series,
                x_labels=[f"Q{index + 1}" for index in range(n_points)],
                legend_labels=[item.name for item in series],
            )
        ],
        style=StyleSpec(font_size=12, palette=_PALETTE[:n_series]),
        knobs={"n_series": n_series, "n_points": n_points, "axis_type": "linear"},
    )
