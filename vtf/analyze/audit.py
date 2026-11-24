"""Deterministic audit sample export."""

import json
import random
from pathlib import Path
from typing import Any


def export_audit_sample(
    rows: list[dict[str, Any]], output_path: Path, *, n: int, seed: int = 7
) -> None:
    """Sample rows reproducibly and write them as JSONL for human review."""

    if n < 0:
        raise ValueError("n must be non-negative")
    if n > len(rows):
        raise ValueError("n cannot exceed row count")
    selected = random.Random(seed).sample(rows, n)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in selected:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
