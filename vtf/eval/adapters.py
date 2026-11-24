"""Model adapter interfaces used by the evaluation harness."""

from pathlib import Path
from typing import Protocol


class ModelAdapter(Protocol):
    """Minimal interface implemented by every multimodal model adapter."""

    def ask(self, image_path: Path, prompt: str) -> str:
        """Return the model's raw answer for an image and prompt."""


class MockModelAdapter:
    """Deterministic adapter for tests and local smoke runs."""

    def __init__(
        self,
        response: str | None = None,
        responses: list[str] | None = None,
    ) -> None:
        if response is None and not responses:
            raise ValueError("provide response or a non-empty responses list")
        if response is not None and responses is not None:
            raise ValueError("provide response or responses, not both")
        self._repeat_response = response
        self._responses = [] if response is not None else list(responses or [])
        self.calls = 0

    def ask(self, image_path: Path, prompt: str) -> str:
        """Read-check the image path and return the next configured response."""

        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        if not prompt.strip():
            raise ValueError("prompt must not be blank")
        if self._repeat_response is None and self.calls >= len(self._responses):
            raise RuntimeError("mock response sequence exhausted")
        response = self._repeat_response if self._repeat_response is not None else self._responses[self.calls]
        self.calls += 1
        return response
