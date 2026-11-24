"""Async, cached, budgeted evaluation runner."""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from vtf.eval.adapters import ModelAdapter
from vtf.eval.budget import Budget
from vtf.eval.cache import DiskCache
from vtf.eval.scorer import ScoreResult, score_task
from vtf.schemas import Task


@dataclass(frozen=True)
class EvaluationResponse:
    """One model response and whether it came from cache."""

    raw_text: str
    cached: bool


@dataclass(frozen=True)
class EvaluationRun:
    """Scored run summary."""

    scores: list[ScoreResult]
    api_calls: int
    cache_hits: int


class EvaluationRunner:
    """Run one adapter with retries, caching, concurrency, and hard budget limits."""

    def __init__(
        self,
        *,
        adapter: ModelAdapter,
        model_name: str,
        cache: DiskCache,
        budget: Budget | None = None,
        max_concurrency: int = 1,
        retries: int = 2,
        cost_per_call_usd: float = 0.0,
    ) -> None:
        if max_concurrency < 1 or retries < 0:
            raise ValueError("max_concurrency must be positive and retries non-negative")
        self.adapter = adapter
        self.model_name = model_name
        self.cache = cache
        self.budget = budget
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.retries = retries
        self.cost_per_call_usd = cost_per_call_usd

    async def evaluate_one(self, image_path: Path, question: str) -> EvaluationResponse:
        """Evaluate one image/prompt, using cache before reserving budget."""

        prompt = f"Answer: <value>\nQuestion: {question}"
        cached = self.cache.get(self.model_name, prompt, image_path)
        if cached is not None:
            return EvaluationResponse(cached, True)
        async with self.semaphore:
            cached = self.cache.get(self.model_name, prompt, image_path)
            if cached is not None:
                return EvaluationResponse(cached, True)
            last_error: Exception | None = None
            for attempt in range(self.retries + 1):
                if self.budget is not None:
                    self.budget.reserve(cost_usd=self.cost_per_call_usd)
                try:
                    raw_text = await asyncio.to_thread(self.adapter.ask, image_path, prompt)
                    self.cache.put(self.model_name, prompt, image_path, raw_text)
                    return EvaluationResponse(raw_text, False)
                except Exception as error:
                    last_error = error
                    if attempt == self.retries:
                        raise
            raise RuntimeError("unreachable") from last_error

    async def evaluate(self, tasks: list[Task]) -> EvaluationRun:
        """Evaluate and score all tasks."""

        responses = await asyncio.gather(
            *(self.evaluate_one(task.image_path, task.question) for task in tasks)
        )
        scores = [score_task(task, response.raw_text) for task, response in zip(tasks, responses)]
        return EvaluationRun(
            scores=scores,
            api_calls=sum(not response.cached for response in responses),
            cache_hits=sum(response.cached for response in responses),
        )
