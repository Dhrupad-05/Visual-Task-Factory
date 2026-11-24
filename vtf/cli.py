"""Typer command-line entry point."""

import typer
from pathlib import Path

from vtf import __version__
from vtf.demo import run_demo
from vtf.report import build_report

app = typer.Typer(help="Visual Task Factory CLI")


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", help="Show the version and exit."),
) -> None:
    """Run Visual Task Factory commands."""

    if version:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def generate(n: int = typer.Option(10, min=1), seed: int = 7) -> None:
    """Placeholder for the Phase 2+ generation pipeline."""

    typer.echo(f"generation is not implemented yet (n={n}, seed={seed})")


@app.command()
def report(output_dir: Path = typer.Option(Path("report"), exists=False)) -> None:
    """Write the static HTML report and findings document."""

    result = build_report(output_dir)
    typer.echo(f"report: {result.html_path}")
    typer.echo(f"findings: {result.findings_path}")


@app.command()
def demo(
    n: int = typer.Option(5, min=1),
    model: str = typer.Option("mock"),
    output_dir: Path = typer.Option(Path("demo"), exists=False),
) -> None:
    """Run the cached local demo without real API calls."""

    result = run_demo(output_dir, n=n, model_name=model)
    typer.echo(f"tasks={result.task_count} api_calls={result.api_calls} cache_hits={result.cache_hits}")
    typer.echo(f"output: {result.output_path}")


if __name__ == "__main__":
    app()
