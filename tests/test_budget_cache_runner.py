import asyncio
from pathlib import Path

import pytest

from vtf.eval.adapters import MockModelAdapter
from vtf.eval.budget import Budget, BudgetExceeded
from vtf.eval.cache import DiskCache
from vtf.eval.runner import EvaluationRunner
from vtf.questions.templates import generate_tasks
from vtf.scene.generator import generate_scene


def test_budget_hard_stop() -> None:
    budget = Budget(max_calls=1, max_spend_usd=0.01)
    budget.reserve(cost_usd=0.01)

    with pytest.raises(BudgetExceeded):
        budget.reserve(cost_usd=0.01)


def test_cache_hit_avoids_adapter_call(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"image")
    cache = DiskCache(tmp_path / "cache")
    adapter = MockModelAdapter(response="Answer: 1")
    first = EvaluationRunner(adapter=adapter, model_name="mock", cache=cache)

    result_one = asyncio.run(first.evaluate_one(image, "Question?"))
    result_two = asyncio.run(first.evaluate_one(image, "Question?"))

    assert result_one.raw_text == result_two.raw_text == "Answer: 1"
    assert adapter.calls == 1
    assert result_two.cached


def test_retry_calls_each_consume_budget(tmp_path: Path) -> None:
    class FlakyAdapter:
        calls = 0

        def ask(self, image_path: Path, prompt: str) -> str:
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("transient")
            return "Answer: 1"

    image = tmp_path / "image.png"
    image.write_bytes(b"image")
    adapter = FlakyAdapter()
    runner = EvaluationRunner(
        adapter=adapter,
        model_name="flaky",
        cache=DiskCache(tmp_path / "cache"),
        budget=Budget(max_calls=2, max_spend_usd=2),
        retries=1,
    )

    result = asyncio.run(runner.evaluate_one(image, "Question?"))

    assert result.raw_text == "Answer: 1"
    assert adapter.calls == 2


def test_mock_integration_is_perfect_then_near_zero_and_rerun_is_cached(tmp_path: Path) -> None:
    image = tmp_path / "image.png"
    image.write_bytes(b"image")
    tasks = generate_tasks(generate_scene(seed=30, chart_type="bar", n_series=2, n_points=3))
    tasks = [task.model_copy(update={"image_path": image}) for task in tasks]
    cache = DiskCache(tmp_path / "cache")

    correct_adapter = MockModelAdapter(responses=[f"{task.reference_answer}" for task in tasks])
    correct_runner = EvaluationRunner(adapter=correct_adapter, model_name="mock-correct", cache=cache)
    correct = asyncio.run(correct_runner.evaluate(tasks))
    assert sum(item.correct for item in correct.scores) == len(tasks)

    wrong_adapter = MockModelAdapter(response="definitely wrong")
    wrong_runner = EvaluationRunner(adapter=wrong_adapter, model_name="mock-wrong", cache=cache)
    wrong = asyncio.run(wrong_runner.evaluate(tasks))
    assert sum(item.correct for item in wrong.scores) == 0

    rerun_adapter = MockModelAdapter(response="should not be called")
    rerun = asyncio.run(
        EvaluationRunner(adapter=rerun_adapter, model_name="mock-correct", cache=cache).evaluate(tasks)
    )
    assert rerun_adapter.calls == 0
    assert rerun.cache_hits == len(tasks)
