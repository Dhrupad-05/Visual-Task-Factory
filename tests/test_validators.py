from pathlib import Path

from vtf.render.boxes import PixelBox
from vtf.schemas import Task
from vtf.validate.ambiguity import validate_choice_margin
from vtf.validate.evidence import validate_evidence
from vtf.validate.necessity import validate_image_necessity
from vtf.validate.reextract import recover_axis_value, validate_reextraction
from vtf.validate.duplicates import duplicate_task_ids


def task(**overrides: object) -> Task:
    values: dict[str, object] = {
        "task_id": "task-1",
        "image_path": Path("image.png"),
        "scene_id": "scene-1",
        "skill": "reading",
        "subskill": "exact_value",
        "question": "What is the value?",
        "answer_type": "numeric",
        "reference_answer": 100,
        "tolerance": 2,
    }
    values.update(overrides)
    return Task(**values)


def test_reextraction_accepts_within_tolerance_and_rejects_wrong_reference() -> None:
    assert validate_reextraction(task(), extracted_answer=101).passed
    wrong = validate_reextraction(task(reference_answer=100), extracted_answer=110)
    assert not wrong.passed
    assert wrong.reason == "reference_mismatch"


def test_pixel_recovery_uses_axis_calibration() -> None:
    # Hand computation: halfway down a 0..100 linear axis is value 50.
    assert recover_axis_value(pixel_y=50, plot_top=0, plot_bottom=100, y_min=0, y_max=100) == 50


def test_ambiguous_bars_fixture_is_rejected() -> None:
    # Golden fixture: 100 versus 99 is a 1% margin, below the 5% threshold.
    result = validate_choice_margin(top=100, second=99, value_range=100, threshold=0.05)

    assert not result.passed
    assert result.reason == "ambiguous_choice"


def test_good_choice_passes_ambiguity_check() -> None:
    assert validate_choice_margin(top=100, second=80, value_range=100, threshold=0.05).passed


def test_clipped_label_fixture_is_rejected() -> None:
    # Golden fixture: the needed tick label extends beyond the right canvas edge.
    result = validate_evidence(
        {"ticks": [PixelBox(95, 10, 110, 20)], "marks": [PixelBox(10, 10, 20, 20)]},
        width=100,
        height=100,
        required_groups=("ticks", "marks"),
    )

    assert not result.passed
    assert result.reason == "box_out_of_canvas"


def test_occluded_series_fixture_is_rejected() -> None:
    # Golden fixture: the target mark is fully covered by the occluding mark.
    result = validate_evidence(
        {"target": [PixelBox(20, 20, 40, 40)], "occluder": [PixelBox(20, 20, 40, 40)]},
        width=100,
        height=100,
        required_groups=("target",),
        occluded_pairs=(("target", "occluder"),),
    )

    assert not result.passed
    assert result.reason == "occluded_element"


def test_good_evidence_fixture_passes() -> None:
    result = validate_evidence(
        {"marks": [PixelBox(10, 10, 20, 20)], "ticks": [PixelBox(10, 80, 20, 90)]},
        width=100,
        height=100,
        required_groups=("marks", "ticks"),
    )

    assert result.passed


def test_text_answerable_fixture_is_flagged() -> None:
    result = validate_image_necessity(task(question="What is the value 100?"))

    assert not result.passed
    assert result.reason == "text_answerable"


def test_non_answerable_question_passes_necessity_check() -> None:
    assert validate_image_necessity(task(question="What is the value?")).passed


def test_duplicate_fixture_is_detected() -> None:
    first = task(task_id="a", question="What is the value?")
    second = task(task_id="b", question=" What is   the value? ")

    assert duplicate_task_ids([first, second]) == {"b": "a"}
