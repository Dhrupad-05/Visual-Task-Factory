from pathlib import Path

from typer.testing import CliRunner

from vtf.cli import app
from vtf.demo import run_demo
from vtf.report import build_report


def test_report_writes_static_html_and_findings(tmp_path: Path) -> None:
    result = build_report(tmp_path, task_count=12, kept_count=10, rejected_count=2)

    assert result.html_path.exists()
    assert result.findings_path.exists()
    html = result.html_path.read_text(encoding="utf-8")
    findings = result.findings_path.read_text(encoding="utf-8")
    assert "Visual Task Factory" in html
    assert "Validity evidence" in html
    assert "Claims to verify" in findings
    assert "synthetic" in findings.lower()


def test_demo_uses_cache_on_rerun(tmp_path: Path) -> None:
    first = run_demo(tmp_path, n=5, model_name="mock")
    second = run_demo(tmp_path, n=5, model_name="mock")

    assert first.task_count == second.task_count == 5
    assert first.api_calls == 5
    assert second.api_calls == 0
    assert second.cache_hits == 5
    assert (tmp_path / "demo.jsonl").exists()


def test_cli_report_and_demo_commands(tmp_path: Path) -> None:
    report = CliRunner().invoke(app, ["report", "--output-dir", str(tmp_path / "report")])
    demo = CliRunner().invoke(app, ["demo", "--n", "2", "--output-dir", str(tmp_path / "demo")])

    assert report.exit_code == 0, report.stdout
    assert demo.exit_code == 0, demo.stdout
    assert (tmp_path / "report" / "report.html").exists()
    assert (tmp_path / "demo" / "demo.jsonl").exists()
