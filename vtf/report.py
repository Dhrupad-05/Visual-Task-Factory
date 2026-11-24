"""Static HTML report and honest findings document generation."""

from dataclasses import dataclass
from html import escape
from pathlib import Path


@dataclass(frozen=True)
class ReportResult:
    """Paths written by report generation."""

    html_path: Path
    findings_path: Path


def build_report(
    output_dir: Path,
    *,
    task_count: int = 0,
    kept_count: int = 0,
    rejected_count: int = 0,
) -> ReportResult:
    """Write a self-contained report with measured and pending metrics separated."""

    if min(task_count, kept_count, rejected_count) < 0:
        raise ValueError("report counts must be non-negative")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "report.html"
    findings_path = output_dir / "findings.md"
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Visual Task Factory report</title>
<style>body{{font:16px system-ui,sans-serif;max-width:960px;margin:2rem auto;line-height:1.5}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:.4rem .7rem}} .note{{background:#fff4cc;padding:.7rem}}</style>
</head><body>
<h1>Visual Task Factory</h1>
<h2>Application story</h2>
<p>Chart-reading errors in finance, healthcare, and operations dashboards can change decisions. This pipeline creates controlled charts whose answers come from the scene specification, then measures which visual traps cause model failures.</p>
<h2>Dataset overview</h2>
<table><tr><th>Metric</th><th>Value</th></tr>
<tr><td>Generated tasks</td><td>{task_count}</td></tr>
<tr><td>Kept tasks</td><td>{kept_count}</td></tr>
<tr><td>Rejected tasks</td><td>{rejected_count}</td></tr></table>
<h2>Validity evidence</h2>
<p>Validator unit tests and golden fixtures are included in the repository. Dataset-level re-extraction, human agreement, and text-only baseline numbers must be supplied from the corresponding run logs before making claims.</p>
<h2>Results and differentiators</h2>
<p>Analysis code supports Wilson intervals, degradation summaries, misconception labels, minimal-pair flip rates, and severity sensitivity. This report does not invent model results when no evaluation artifact was supplied.</p>
<h2>Limitations</h2>
<ul><li>Synthetic charts are not a substitute for real dashboard images.</li><li>The current renderer is primarily single-panel bar, line, and scatter.</li><li>Real-provider evaluation and human audits require operator credentials and review.</li></ul>
<p class="note">See <a href="findings.md">findings.md</a> for claims that still require verification.</p>
</body></html>"""
    html_path.write_text(html, encoding="utf-8")
    findings = f"""# Findings

This report was generated from the Visual Task Factory pipeline. It describes a synthetic benchmark, not measured real-world model performance. Counts supplied to this run: generated `{task_count}`, kept `{kept_count}`, rejected `{rejected_count}`.

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
"""
    findings_path.write_text(findings, encoding="utf-8")
    return ReportResult(html_path, findings_path)
