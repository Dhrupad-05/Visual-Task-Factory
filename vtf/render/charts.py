"""Deterministic Matplotlib chart renderer."""

from dataclasses import dataclass
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

from vtf.render.boxes import PixelBox
from vtf.render.effects import apply_effects
from vtf.schemas import SceneSpec


@dataclass(frozen=True)
class RenderResult:
    """Rendered image dimensions and named pixel evidence."""

    image_path: Path
    width: int
    height: int
    boxes: dict[str, list[PixelBox]]


def _display_box_to_pixel_box(
    bounds: tuple[float, float, float, float], width: int, height: int
) -> PixelBox:
    x, y, box_width, box_height = bounds
    if not all(math.isfinite(value) for value in bounds):
        return PixelBox(0.0, 0.0, 0.0, 0.0)
    return PixelBox(x, height - (y + box_height), x + box_width, height - y).clipped(
        width, height
    )


def _record_artist_box(artist: object, renderer: object, width: int, height: int) -> PixelBox:
    bounds = artist.get_window_extent(renderer).bounds  # type: ignore[attr-defined]
    return _display_box_to_pixel_box(bounds, width, height)


def render_scene(
    scene: SceneSpec,
    output_path: Path,
    *,
    width: int = 800,
    height: int = 600,
) -> RenderResult:
    """Render a scene spec and record mark, tick, label, and legend boxes."""

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel = scene.panels[0]
    dpi = 100
    figure, axis = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
    try:
        figure.patch.set_facecolor("white")
        axis.set_facecolor("white")
        axis.set_ylim(panel.axes.y_min, panel.axes.y_max)
        if panel.axes.y_type == "log":
            axis.set_yscale("log")
        if scene.style.grid:
            axis.grid(True, alpha=0.25)
        x_values = np.arange(len(panel.series[0].values))
        mark_artists: list[object] = []
        colors = scene.style.palette or [series.color for series in panel.series]
        if scene.chart_type == "bar":
            group_width = 0.8
            bar_width = group_width / len(panel.series)
            for series_index, series in enumerate(panel.series):
                positions = x_values - group_width / 2 + bar_width * (series_index + 0.5)
                bars = axis.bar(
                    positions,
                    series.values,
                    width=bar_width,
                    color=colors[series_index],
                    label=series.name,
                )
                mark_artists.extend(bars.patches)
        else:
            for series in panel.series:
                if scene.chart_type == "line":
                    axis.plot(
                        x_values,
                        series.values,
                        marker=series.marker,
                        color=colors[panel.series.index(series)],
                        label=series.name,
                    )
                else:
                    points = axis.scatter(
                        x_values,
                        series.values,
                        color=colors[panel.series.index(series)],
                        marker=series.marker,
                        label=series.name,
                    )
                    mark_artists.append(points)
        axis.set_xticks(x_values)
        axis.set_xticklabels(panel.x_labels or [str(x) for x in x_values])
        axis.tick_params(labelsize=scene.style.font_size)
        legend = axis.legend() if panel.legend_labels or len(panel.series) > 1 else None
        figure.tight_layout()
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        boxes: dict[str, list[PixelBox]] = {"marks": [], "ticks": [], "labels": [], "legend": []}
        if scene.chart_type == "line":
            for series in panel.series:
                for x_value, y_value in zip(x_values, series.values):
                    display_x, display_y = axis.transData.transform((x_value, y_value))
                    radius = max(2.0, scene.style.font_size / 2)
                    boxes["marks"].append(
                        _display_box_to_pixel_box(
                            (display_x - radius, display_y - radius, radius * 2, radius * 2),
                            width,
                            height,
                        )
                    )
        elif scene.chart_type == "scatter":
            for artist in mark_artists:
                boxes["marks"].extend(
                    [_record_artist_box(artist, renderer, width, height)] * len(panel.series[0].values)
                )
        else:
            for artist in mark_artists:
                boxes["marks"].append(_record_artist_box(artist, renderer, width, height))
        boxes["ticks"] = [
            _record_artist_box(label, renderer, width, height)
            for label in [*axis.get_xticklabels(), *axis.get_yticklabels()]
            if label.get_text()
        ]
        boxes["labels"] = (
            [_record_artist_box(axis.xaxis.label, renderer, width, height)]
            if axis.xaxis.label.get_text()
            else []
        )
        if legend is not None:
            boxes["legend"] = [
                _record_artist_box(text, renderer, width, height) for text in legend.get_texts()
            ]
        raw = figure.canvas.buffer_rgba().tobytes()
        raw = apply_effects(
            raw,
            width=width,
            height=height,
            noise=scene.style.noise,
            seed=scene.seed,
        )
        image = np.frombuffer(raw, dtype=np.uint8).reshape((height, width, 4))
        mpimg.imsave(output_path, image, format="png", metadata={"Software": "Visual Task Factory"})
    finally:
        plt.close(figure)
    return RenderResult(output_path, width, height, boxes)
