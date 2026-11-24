from typer.testing import CliRunner

from vtf.cli import app


def test_cli_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "0.1.0"


def test_cli_generate_skeleton() -> None:
    result = CliRunner().invoke(app, ["generate", "--n", "3", "--seed", "11"])

    assert result.exit_code == 0
    assert "n=3, seed=11" in result.stdout
