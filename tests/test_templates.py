from vtf.questions.templates import generate_tasks
from vtf.scene.generator import generate_scene


def test_all_six_skill_templates_render_well_formed_tasks() -> None:
    scene = generate_scene(seed=12, chart_type="line", n_series=3, n_points=5)
    tasks = generate_tasks(scene)

    assert {task.skill for task in tasks} == {
        "reading",
        "comparison",
        "relational",
        "multi_step",
        "trap_detection",
        "robustness",
    }
    assert all(task.question.endswith("?") for task in tasks)
    assert all(task.reference_answer is not None for task in tasks)
    assert all(task.scene_id == scene.id for task in tasks)


def test_template_generation_is_deterministic() -> None:
    scene = generate_scene(seed=13, chart_type="bar", n_series=2, n_points=4)

    assert generate_tasks(scene) == generate_tasks(scene)
