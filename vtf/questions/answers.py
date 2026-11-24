"""Pure reference-answer functions derived only from a :class:`SceneSpec`."""

import math

from vtf.schemas import SceneSpec


def answer_reading(scene: SceneSpec, *, series_index: int, point_index: int, panel_index: int = 0) -> float:
    """Return one plotted value from the scene data."""

    return scene.panels[panel_index].series[series_index].values[point_index]


def answer_highest_series(scene: SceneSpec, *, point_index: int, panel_index: int = 0) -> str:
    """Return the name of the series with the highest value at an x position."""

    series = scene.panels[panel_index].series
    return max(series, key=lambda item: item.values[point_index]).name


def answer_largest_panel(scene: SceneSpec, *, series_index: int, point_index: int = 0) -> int:
    """Return the zero-based panel containing the largest requested value."""

    return max(
        range(len(scene.panels)),
        key=lambda panel_index: scene.panels[panel_index].series[series_index].values[point_index],
    )


def answer_legend_series(scene: SceneSpec, *, series_index: int, panel_index: int = 0) -> str:
    """Return the series name represented by a legend entry."""

    return scene.panels[panel_index].series[series_index].name


def answer_crossing_x(
    scene: SceneSpec,
    *,
    first_series: int,
    second_series: int,
    panel_index: int = 0,
) -> float:
    """Return the first x index where two series meet, interpolating crossings."""

    panel = scene.panels[panel_index]
    first = panel.series[first_series].values
    second = panel.series[second_series].values
    for index, (left, right) in enumerate(zip(first, second)):
        if left == right:
            return float(index)
        if index + 1 < len(first):
            next_difference = first[index + 1] - second[index + 1]
            difference = left - right
            if difference * next_difference < 0:
                return index + (-difference / (next_difference - difference))
    raise ValueError("series do not cross")


def answer_percent_change(
    scene: SceneSpec,
    *,
    series_index: int,
    first_point: int,
    last_point: int,
    panel_index: int = 0,
) -> float:
    """Return percent change between two values."""

    first = answer_reading(scene, series_index=series_index, point_index=first_point, panel_index=panel_index)
    last = answer_reading(scene, series_index=series_index, point_index=last_point, panel_index=panel_index)
    if first == 0:
        raise ValueError("percent change is undefined when the starting value is zero")
    return (last - first) / abs(first) * 100


def answer_truncated(scene: SceneSpec, *, panel_index: int = 0) -> bool:
    """Return whether the panel has a truncated vertical axis."""

    return scene.panels[panel_index].axes.truncated or scene.panels[panel_index].axes.y_min > 0


def answer_exaggerates_change(scene: SceneSpec, *, panel_index: int = 0) -> bool:
    """Return whether the chart's axis makes bar changes visually exaggerated."""

    panel = scene.panels[panel_index]
    return scene.chart_type == "bar" and answer_truncated(scene, panel_index=panel_index)


def misconception_log_read_as_linear(
    scene: SceneSpec, *, series_index: int, point_index: int, panel_index: int = 0
) -> float:
    """Map a log-positioned value onto a linear axis as a controlled misread."""

    panel = scene.panels[panel_index]
    if panel.axes.y_type != "log":
        raise ValueError("log_read_as_linear only applies to log axes")
    value = answer_reading(scene, series_index=series_index, point_index=point_index, panel_index=panel_index)
    log_min = math.log10(panel.axes.y_min)
    log_max = math.log10(panel.axes.y_max)
    fraction = (math.log10(value) - log_min) / (log_max - log_min)
    return panel.axes.y_min + fraction * (panel.axes.y_max - panel.axes.y_min)
