import hashlib
from pathlib import Path

import matplotlib.image as mpimg

from vtf.render.charts import render_scene
from vtf.scene.generator import generate_scene


def test_renderer_is_deterministic_and_matches_config(tmp_path: Path) -> None:
    scene = generate_scene(seed=5, chart_type="bar", n_series=2, n_points=5)
    first_path = tmp_path / "first.png"
    second_path = tmp_path / "second.png"

    first = render_scene(scene, first_path, width=640, height=480)
    second = render_scene(scene, second_path, width=640, height=480)

    assert hashlib.sha256(first_path.read_bytes()).digest() == hashlib.sha256(
        second_path.read_bytes()
    ).digest()
    assert first.width == second.width == 640
    assert first.height == second.height == 480
    assert mpimg.imread(first_path).shape[:2] == (480, 640)


def test_renderer_records_mark_counts_and_in_canvas_boxes(tmp_path: Path) -> None:
    for chart_type in ("bar", "line", "scatter"):
        scene = generate_scene(seed=8, chart_type=chart_type, n_series=2, n_points=4)
        result = render_scene(scene, tmp_path / f"{chart_type}.png", width=500, height=400)

        expected_marks = len(scene.panels[0].series) * len(scene.panels[0].series[0].values)
        assert len(result.boxes["marks"]) == expected_marks
        assert all(
            0 <= box.x0 <= box.x1 <= result.width
            and 0 <= box.y0 <= box.y1 <= result.height
            for boxes in result.boxes.values()
            for box in boxes
        )
