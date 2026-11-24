from pathlib import Path

from vtf.eval.scorer import score_task
from vtf.schemas import Task


def make_task(answer_type: str, reference: object, tolerance: float | None = None, **kwargs: object) -> Task:
    return Task(
        task_id="score",
        image_path=Path("image.png"),
        scene_id="scene",
        skill="reading",
        subskill="test",
        question="Question?",
        answer_type=answer_type,
        reference_answer=reference,
        tolerance=tolerance,
        **kwargs,
    )


def test_numeric_parser_handles_units_and_junk() -> None:
    assert score_task(make_task("numeric", 1200, tolerance=0), "Answer: 1,200").correct
    assert score_task(make_task("numeric", 12, tolerance=0), "12%").correct
    assert score_task(make_task("numeric", 3500, tolerance=0), "$3.5k").correct
    junk = score_task(make_task("numeric", 10, tolerance=1), "not a number")
    assert not junk.correct and junk.format_failure


def test_yes_no_and_choice_normalization() -> None:
    yes = make_task("yes_no", True)
    choice = make_task("choice", "Series A", choices=["Series A", "Series B"])

    assert score_task(yes, "Yes, the answer is yes").correct
    assert score_task(choice, "Answer: series a").correct
