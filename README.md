# Visual Task Factory

Visual Task Factory generates deterministic synthetic chart images, questions,
spec-derived reference answers, misconception distractors, controlled minimal
pairs, and evaluation analysis.

## Quick start

Requires Python 3.11–3.13.

```powershell
python -m pip install -r requirements.txt
pytest
python -m vtf.cli demo --n 5
python -m vtf.cli report
```

The demo uses a deterministic mock adapter and a disk cache. It does not call a
real model provider or spend money. Re-running it with the same output directory
should produce cache hits and zero new adapter calls.

## What is implemented

- Seeded bar, line, and scatter scene generation and deterministic rendering.
- Pixel evidence boxes and validation checks.
- Six question skill categories with pure reference-answer computation.
- Misconception distractors with collision filtering.
- Minimal pairs, cached evaluation, hard budgets, type-aware scoring, and severity.
- Wilson intervals, degradation summaries, failure classification, pair metrics,
  severity sensitivity, and audit export.

## Honest limitations

The current implementation is a controlled synthetic benchmark, not a claim about
real-world dashboard performance. It has limited chart-family and panel coverage;
real-provider evaluation, human spot checks, and final headline findings require
operator-supplied credentials, approved spend, and manual review.

Before publishing results, use the `report/findings.md` claims-to-verify list and
replace only those items supported by recorded run artifacts.
