from pathlib import Path

from vtf.render.boxes import PixelBox
from vtf.schemas import Task
from vtf.validate.pipeline import validate_task


def _task(
    reference: object = 10, question: str = "What is the value?", tolerance: float = 1
) -> Task:
    return Task(
        task_id="fixture",
        image_path=Path("image.png"),
        scene_id="scene",
        skill="reading",
        subskill="exact_value",
        question=question,
        answer_type="numeric",
        reference_answer=reference,
        tolerance=tolerance,
    )


def test_all_documented_golden_fixtures_classify_correctly() -> None:
    fixtures = {
        "ambiguous_bars": validate_task(
            _task(),
            extracted_answer=10,
            choice_values=(100, 99, 100),
        ),
        "clipped_label": validate_task(
            _task(),
            extracted_answer=10,
            evidence={"ticks": [PixelBox(95, 0, 110, 10)]},
            canvas=(100, 100),
            required_evidence=("ticks",),
        ),
        "occluded_series": validate_task(
            _task(),
            extracted_answer=10,
            evidence={"target": [PixelBox(10, 10, 20, 20)], "occluder": [PixelBox(10, 10, 20, 20)]},
            canvas=(100, 100),
            required_evidence=("target",),
            occluded_pairs=(("target", "occluder"),),
        ),
        "wrong_reference": validate_task(
            _task(reference=11, tolerance=0.5), extracted_answer=10
        ),
        "text_answerable": validate_task(_task(question="What is the value 10?"), extracted_answer=10),
        "good_task": validate_task(
            _task(),
            extracted_answer=10,
            evidence={"marks": [PixelBox(10, 10, 20, 20)]},
            canvas=(100, 100),
            required_evidence=("marks",),
        ),
    }

    assert not fixtures["ambiguous_bars"].passed
    assert not fixtures["clipped_label"].passed
    assert not fixtures["occluded_series"].passed
    assert not fixtures["wrong_reference"].passed
    assert not fixtures["text_answerable"].passed
    assert fixtures["good_task"].passed
