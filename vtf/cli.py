"""Typer command-line entry point."""

import typer

from vtf import __version__

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


if __name__ == "__main__":
    app()
