from vtf.questions.misconceptions import compute_distractors, filter_distractors
from vtf.questions.templates import generate_tasks
from vtf.scene.generator import generate_scene


def test_collision_rule_drops_truth_and_duplicate_distractors() -> None:
    # Hand computation: truth=10; 10 collides with truth and 20 collides with
    # the first retained distractor within tolerance 1, so only 12 remains.
    result = filter_distractors(
        truth=10,
        candidates={"truth_copy": 10, "near_truth": 10.5, "near_other": 11, "valid": 12},
        tolerance=1,
    )

    assert result == {"valid": 12}


def test_inapplicable_log_misconception_is_omitted() -> None:
    scene = generate_scene(seed=14, chart_type="bar", n_series=2, n_points=3)
    task = generate_tasks(scene)[0]

    distractors = compute_distractors(scene, task)

    assert "log_read_as_linear" not in distractors


def test_log_misconception_is_present_for_log_reading() -> None:
    scene = generate_scene(seed=15, chart_type="line", n_series=2, n_points=3)
    scene.panels[0].axes.y_type = "log"
    task = generate_tasks(scene)[0]

    distractors = compute_distractors(scene, task)

    assert "log_read_as_linear" in distractors
    assert distractors["log_read_as_linear"] != task.reference_answer


def test_choice_tasks_get_meaningful_wrong_series_distractors() -> None:
    scene = generate_scene(seed=16, chart_type="bar", n_series=2, n_points=3)
    comparison = generate_tasks(scene)[1]

    assert comparison.distractors["wrong_series"] in comparison.choices
    assert comparison.distractors["wrong_series"] != comparison.reference_answer
