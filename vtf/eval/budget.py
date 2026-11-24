"""Hard evaluation budget enforcement."""


class BudgetExceeded(RuntimeError):
    """Raised before a call that would exceed the configured hard cap."""


class Budget:
    """Track API calls and estimated spend without permitting overspend."""

    def __init__(self, *, max_calls: int, max_spend_usd: float) -> None:
        if max_calls < 0 or max_spend_usd < 0:
            raise ValueError("budget limits must be non-negative")
        self.max_calls = max_calls
        self.max_spend_usd = max_spend_usd
        self.calls = 0
        self.spend_usd = 0.0

    def reserve(self, *, cost_usd: float) -> None:
        """Reserve one call or raise before state changes."""

        if cost_usd < 0:
            raise ValueError("cost_usd must be non-negative")
        if self.calls + 1 > self.max_calls:
            raise BudgetExceeded("maximum API call count reached")
        if self.spend_usd + cost_usd > self.max_spend_usd + 1e-12:
            raise BudgetExceeded("maximum API spend reached")
        self.calls += 1
        self.spend_usd += cost_usd
