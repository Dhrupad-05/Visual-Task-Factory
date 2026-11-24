from pathlib import Path

from vtf.eval.severity import decision_weighted_accuracy, severity_score
from vtf.schemas import Task


def test_severity_numeric_is_capped_and_correct_is_zero() -> None:
    task = Task(
        task_id="severity",
        image_path=Path("image.png"),
        scene_id="scene",
        skill="reading",
        subskill="test",
        question="Question?",
        answer_type="numeric",
        reference_answer=10,
        distractors={"order_error": 100},
    )

    assert severity_score(task, 10) == 0
    assert severity_score(task, 100) == 1
    assert severity_score(task, 1000) == 1


def test_decision_weighted_accuracy_is_one_for_all_correct() -> None:
    assert decision_weighted_accuracy([0, 0, 0]) == 1
