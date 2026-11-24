from pathlib import Path

from vtf.eval.scorer import score_task
from vtf.schemas import Task
from vtf.analyze.stats import accuracy_by_knob, wilson_interval
from vtf.analyze.classify import classify_prediction
from vtf.analyze.pairs import PairOutcome, analyze_pairs
from vtf.analyze.severity import rank_models
from vtf.analyze.audit import export_audit_sample


def numeric_task(**kwargs: object) -> Task:
    values: dict[str, object] = {
        "task_id": "task",
        "image_path": Path("image.png"),
        "scene_id": "scene",
        "skill": "reading",
        "subskill": "exact_value",
        "question": "Question?",
        "answer_type": "numeric",
        "reference_answer": 10,
        "tolerance": 0.1,
        "distractors": {"log_read_as_linear": 50, "wrong_series": 5},
        "difficulty": {"noise": "heavy"},
    }
    values.update(kwargs)
    return Task(**values)


def test_wilson_interval_and_knob_accuracy() -> None:
    low, high = wilson_interval(5, 10)
    assert 0 < low < 0.5 < high < 1

    tasks = [numeric_task(task_id=f"{i}", difficulty={"noise": "light" if i < 2 else "heavy"}) for i in range(4)]
    scores = [score_task(task, "10") for task in tasks]
    summaries = accuracy_by_knob(tasks, scores, knob="noise")

    assert summaries["light"].total == 2
    assert summaries["light"].correct == 2
    assert summaries["heavy"].accuracy == 1


def test_classifier_labels_distractor_other_ambiguous_and_format() -> None:
    task = numeric_task()
    assert classify_prediction(task, "50").label == "log_read_as_linear"
    assert classify_prediction(task, "99").label == "other"
    ambiguous = numeric_task(distractors={"first": 5, "second": 5.05})
    assert classify_prediction(ambiguous, "5").label == "ambiguous"
    assert classify_prediction(task, "not parseable").label == "format_failure"


def test_pair_flip_rate_and_accuracy_delta() -> None:
    outcomes = [
        PairOutcome("p1", "axis_type", True, False),
        PairOutcome("p2", "axis_type", True, True),
    ]
    summary = analyze_pairs(outcomes)["axis_type"]

    assert summary.flip_rate == 0.5
    assert summary.accuracy_delta == -0.5


def test_severity_ranking_sensitivity_and_audit_export(tmp_path: Path) -> None:
    cases = {"model-a": [(numeric_task(), 10)], "model-b": [(numeric_task(), 50)]}
    ranking = rank_models(cases, distractor_penalty=1.5)
    assert ranking[0][0] == "model-a"
    rankings = [
        rank_models(cases, distractor_penalty=penalty)
        for penalty in (1.0, 1.5, 2.0)
    ]
    assert all(ranking[0][0] == "model-a" for ranking in rankings)

    output = tmp_path / "audit.jsonl"
    export_audit_sample([{"task_id": str(i), "label": "other"} for i in range(5)], output, n=3, seed=2)
    assert len(output.read_text(encoding="utf-8").splitlines()) == 3
