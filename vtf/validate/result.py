"""Common validator result type."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    """A validator decision with a stable rejection reason."""

    passed: bool
    reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, **details: Any) -> "ValidationResult":
        """Create a passing result."""

        return cls(True, None, details)

    @classmethod
    def reject(cls, reason: str, **details: Any) -> "ValidationResult":
        """Create a rejected result."""

        return cls(False, reason, details)
