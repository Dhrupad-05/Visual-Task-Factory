from pathlib import Path

import pytest
from pydantic import ValidationError

from vtf.schemas import (
    AxisSpec,
    PanelSpec,
    SceneSpec,
    SeriesSpec,
    StyleSpec,
    Task,
)


def sample_scene() -> SceneSpec:
    return SceneSpec(
        id="scene-1",
        seed=7,
        chart_type="bar",
        panels=[
            PanelSpec(
                axes=AxisSpec(x_type="categorical", y_type="linear", y_min=0, y_max=10),
                series=[
                    SeriesSpec(name="Revenue", color="#3366cc", values=[2, 4, 8]),
                ],
                legend_labels=["Revenue"],
            )
        ],
        style=StyleSpec(font_size=12, palette=["#3366cc"]),
        knobs={"n_series": 1, "axis_type": "linear"},
    )


def test_scene_spec_accepts_required_structure_and_is_json_serializable() -> None:
    scene = sample_scene()

    assert scene.panels[0].series[0].values == [2, 4, 8]
    assert scene.model_dump_json()


def test_scene_spec_rejects_invalid_axis_range() -> None:
    with pytest.raises(ValidationError):
        AxisSpec(x_type="categorical", y_type="linear", y_min=10, y_max=0)


def test_task_contains_differentiator_fields() -> None:
    task = Task(
        task_id="task-1",
        image_path=Path("data/images/scene-1.png"),
        scene_id="scene-1",
        skill="reading",
        subskill="exact_value",
        question="What is the value?",
        answer_type="numeric",
        reference_answer=8,
        distractors={"off_by_tick": 7},
        pair_id="pair-1",
        variant_of="task-0",
        factor_changed="axis_type",
        severity_params={"trap_type": "none", "scale": 1.0},
    )

    assert task.distractors["off_by_tick"] == 7
    assert task.pair_id == "pair-1"
    assert task.severity_params["scale"] == 1.0


def test_task_rejects_empty_identity_fields() -> None:
    with pytest.raises(ValidationError):
        Task(
            task_id="",
            image_path="image.png",
            scene_id="scene-1",
            skill="reading",
            subskill="exact_value",
            question="What is the value?",
            answer_type="numeric",
            reference_answer=8,
            severity_params={},
        )
