# src/dfguard/cli.py

from __future__ import annotations

import sys
from pathlib import Path

import typer

from .profiler import quick_profile
from .core import validate_profile

app = typer.Typer(help="DfGuard - Data validation CLI")


@app.command()
def main(
    path: str = typer.Argument(..., help="Path to CSV or Parquet file"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON instead of text"),
):
    """
    CLI entrypoint.
    Matches the behavior expected by tests in tests/test_cli.py.
    """

    file_path = Path(path)

    # File must exist
    if not file_path.exists():
        typer.echo(f"Error: file not found: {file_path}", err=True)
        raise typer.Exit(code=1)

    # Profile must succeed
    try:
        profile = quick_profile(str(file_path))
        df = profile["df"]
    except Exception as exc:
        typer.echo(f"Error: failed to read file: {exc}", err=True)
        raise typer.Exit(code=1)

    # Run validation
    report = validate_profile(profile)

    # JSON MODE -----------------------------------------------------
    if json_output:
        # Must print ONLY JSON. No extra lines.
        typer.echo(report.to_json())
        raise typer.Exit(code=0)

    # TEXT MODE -----------------------------------------------------
    # Tests expect "Rows:" somewhere in output.
    typer.echo(f"Reading: {file_path}")
    typer.echo(f"Rows: {profile.get('rows')}")
    typer.echo(f"Columns: {profile.get('columns')}")
    typer.echo(f"Status: {report.status}")

    raise typer.Exit(code=0)


# Allow: python -m dfguard.cli file.csv
if __name__ == "__main__":
    app()
