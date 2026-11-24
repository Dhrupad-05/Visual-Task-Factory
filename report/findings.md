# Findings

This report was generated from the Visual Task Factory pipeline. It describes a synthetic benchmark, not measured real-world model performance. Counts supplied to this run: generated `0`, kept `0`, rejected `0`.

## Current evidence

- The code-level validator suite and golden fixtures pass locally.
- Reference answers are computed from scene specifications through pure functions.
- Model/API results are not claimed here unless an evaluation artifact is supplied.

## Claims to verify

Before submission, verify each claim against the named source:

1. Dataset size and rejection funnel — generation and validation JSONL/logs.
2. Re-extraction agreement — validator run output; target is at least 98%.
3. Human agreement — stratified 30–50 task spot check; target is at least 95%.
4. Text-only baseline — per-skill baseline output and chance calculation.
5. Model accuracy and confidence intervals — scored prediction files and analyzer output.
6. Misconception shares — classifier output plus the 50-example audit.
7. Minimal-pair flip rates — pair analysis output and pair-integrity audit.
8. Severity ranking stability — three-constant sensitivity output.

Do not replace these placeholders with estimates or mock results.
